from .constants import SUPPORTED_GRADES
from .formatters import format_remarks, humanize_status


def next_school_year(school_year):
    start, end = school_year.split("-")
    return f"{int(start) + 1}-{int(end) + 1}"


def build_expected_path(start_year, start_grade):
    path = []
    current_year = start_year

    for grade in range(start_grade, 11):
        path.append({"grade": grade, "school_year": current_year})
        current_year = next_school_year(current_year)

    return path


def is_transfer_in_status(status):
    return status in {"TRANSFER_IN", "PENDING_TRANSFER_IN"}


def is_missing_status(status):
    return status == "MISSING"


def is_active_enrollment_status(status):
    return status not in {"MISSING", "TRANSFER_OUT"}


def get_completion_status(record):
    if isinstance(record, dict):
        if record.get("grade_level") == 10 or record.get("expected_grade") == 10:
            return record.get("completion_status") or "PASS"

        return record.get("completion_status") or ""

    if len(record) > 4:
        return record[4] or ("PASS" if len(record) > 1 and record[1] == 10 else "")

    return ""


def is_completer_record(record):
    # LIS/SF1 imports do not provide a separate graduation field yet.
    # A Grade 10 record must now be marked PASS to count as a completer.
    return (
        record["grade_level"] == 10
        and is_active_enrollment_status(record["status"])
        and get_completion_status(record) == "PASS"
    )


def is_survival_record(record):
    return (
        record["grade_level"] == 10
        and is_active_enrollment_status(record["status"])
        and get_completion_status(record) == "FAIL"
    )


def summarize_cohort_status(path_cells, records=None):
    records = records or []
    statuses = [cell["status"] for cell in path_cells if not is_missing_status(cell["status"])]
    all_statuses = statuses + [record[2] for record in records if not is_missing_status(record[2])]
    grades = [
        cell["actual_grade"]
        for cell in path_cells
        if cell["actual_grade"] is not None and not is_missing_status(cell["status"])
    ]
    all_grades = [record[1] for record in records if is_active_enrollment_status(record[2])]
    has_missing = any(cell["status"] == "MISSING" for cell in path_cells)
    has_grade_10_pass = any(record[1] == 10 and record[2] != "TRANSFER_OUT" and get_completion_status(record) == "PASS" for record in records)
    has_grade_10_fail = any(record[1] == 10 and record[2] != "TRANSFER_OUT" and get_completion_status(record) == "FAIL" for record in records)
    has_grade_10_pending = any(
        record[1] == 10
        and is_active_enrollment_status(record[2])
        and get_completion_status(record) not in {"PASS", "FAIL"}
        for record in records
    )

    if "TRANSFER_OUT" in all_statuses:
        return "TRANSFER_OUT"

    if has_grade_10_pass:
        return "DELAYED_COMPLETED" if has_missing else "COMPLETED"

    if has_grade_10_fail:
        return "SURVIVED"

    if has_grade_10_pending:
        return "GRADE10_PENDING"

    if "TRANSFER_IN" in all_statuses or "PENDING_TRANSFER_IN" in all_statuses:
        return "TRANSFER_IN"

    if len(grades) != len(set(grades)) or len(all_grades) != len(set(all_grades)):
        return "REPEATED"

    if has_missing:
        return "INCOMPLETE"

    return "STRAIGHT_PATH"


def build_cohort_tracking(cursor, start_year, start_grade, expected_path):
    cursor.execute(
        """
        SELECT DISTINCT s.lrn, s.name
        FROM students s
        JOIN student_records r ON s.lrn = r.lrn
        WHERE r.school_year = %s
        AND r.grade_level = %s
        ORDER BY s.name
        """,
        (start_year, start_grade),
    )
    cohort_students = cursor.fetchall()

    rows = []
    summary = {
        "total": len(cohort_students),
        "straight_path": 0,
        "completed": 0,
        "delayed": 0,
        "repeated": 0,
        "transfer_in": 0,
        "transfer_out": 0,
        "survived": 0,
        "dropped": 0,
        "incomplete": 0,
        "for_review": 0,
        "path_counts": {},
    }

    for lrn, name in cohort_students:
        cursor.execute(
            """
            SELECT school_year, grade_level, status, remarks, completion_status
            FROM student_records
            WHERE lrn = %s
            AND grade_level BETWEEN %s AND 10
            ORDER BY school_year, grade_level
            """,
            (lrn, start_grade),
        )
        records = cursor.fetchall()
        records_by_year_grade = {
            (school_year, grade_level): {
                "status": status,
                "remarks": remarks,
                "grade": grade_level,
                "completion_status": completion_status or ("PASS" if grade_level == 10 else ""),
            }
            for school_year, grade_level, status, remarks, completion_status in records
        }

        path_cells = []

        for step in expected_path:
            record = records_by_year_grade.get((step["school_year"], step["grade"]))

            if record and not is_missing_status(record["status"]):
                path_cells.append(
                    {
                        "school_year": step["school_year"],
                        "expected_grade": step["grade"],
                        "actual_grade": record["grade"],
                        "status": record["status"],
                        "status_label": humanize_status(record["status"]),
                        "completion_status": get_completion_status(record),
                        "remarks": format_remarks(record["status"], record["remarks"]),
                    }
                )
            else:
                path_cells.append(
                    {
                        "school_year": step["school_year"],
                        "expected_grade": step["grade"],
                        "actual_grade": None,
                        "status": "MISSING",
                        "status_label": humanize_status("MISSING"),
                        "completion_status": "",
                        "remarks": "",
                    }
                )

        result = summarize_cohort_status(path_cells, records)

        if result == "COMPLETED":
            summary["completed"] += 1
            summary["straight_path"] += 1
        elif result == "DELAYED_COMPLETED":
            summary["completed"] += 1
            summary["delayed"] += 1
        elif result == "STRAIGHT_PATH":
            summary["straight_path"] += 1
        elif result == "REPEATED":
            summary["repeated"] += 1
        elif result == "TRANSFER_IN":
            summary["transfer_in"] += 1
        elif result == "TRANSFER_OUT":
            summary["transfer_out"] += 1
        elif result == "SURVIVED":
            summary["survived"] += 1
        else:
            summary["incomplete"] += 1

        if result == "INCOMPLETE" and any(cell["status"] == "MISSING" for cell in path_cells):
            summary["dropped"] += 1

        if result not in {"COMPLETED", "STRAIGHT_PATH"}:
            summary["for_review"] += 1

        rows.append(
            {
                "lrn": lrn,
                "name": name,
                "path": path_cells,
                "result": result,
                "result_label": humanize_status(result),
            }
        )

    for step in expected_path:
        summary["path_counts"][f"{step['grade']}|{step['school_year']}"] = sum(
            1
            for row in rows
            for cell in row["path"]
            if cell["expected_grade"] == step["grade"]
            and cell["school_year"] == step["school_year"]
            and cell["status"] not in {"MISSING", "TRANSFER_OUT"}
        )

    return rows, summary


def build_grade7_cohort_report(cursor, start_year, start_grade=7):
    expected_path = build_expected_path(start_year, start_grade)
    end_year = expected_path[-1]["school_year"]
    transition_breakdown = [
        {
            "school_year": step["school_year"],
            "grade": step["grade"],
            "previous_school_year": expected_path[index]["school_year"],
            "previous_grade": expected_path[index]["grade"],
            "previous_enrollment": 0,
            "retained": 0,
            "current_students": 0,
            "repeated": 0,
            "retention_rate": 0,
            "repetition_rate": 0,
        }
        for index, step in enumerate(expected_path[1:])
    ]
    transition_totals = {
        "previous_enrollment": 0,
        "retained": 0,
        "current_students": 0,
        "repeated": 0,
    }

    cursor.execute(
        """
        SELECT DISTINCT s.lrn, s.name
        FROM students s
        JOIN student_records r ON s.lrn = r.lrn
        WHERE r.school_year = %s
        AND r.grade_level = %s
        ORDER BY s.name
        """,
        (start_year, start_grade),
    )
    cohort_students = cursor.fetchall()

    summary = {
        "total": len(cohort_students),
        "on_time": 0,
        "completed": 0,
        "grade10_enrollment": 0,
        "grade10_completers": 0,
        "survival": 0,
        "survived": 0,
        "delayed": 0,
        "repeated": 0,
        "transfer_out": 0,
        "incomplete": 0,
        "for_review": 0,
    }
    breakdown = {
        grade: {
            "grade": grade,
            "missing": 0,
            "repeated_or_delayed": 0,
            "transferred_out": 0,
            "for_review": 0,
        }
        for grade in SUPPORTED_GRADES
    }
    review_learners = []
    rows = []

    for lrn, name in cohort_students:
        cursor.execute(
            """
            SELECT school_year, grade_level, status, remarks, completion_status
            FROM student_records
            WHERE lrn = %s
            AND grade_level BETWEEN %s AND 10
            ORDER BY school_year, grade_level
            """,
            (lrn, start_grade),
        )
        records = [
            {
                "school_year": school_year,
                "grade_level": grade_level,
                "status": status,
                "remarks": remarks,
                "completion_status": completion_status or ("PASS" if grade_level == 10 else ""),
            }
            for school_year, grade_level, status, remarks, completion_status in cursor.fetchall()
        ]
        records_by_year_grade = {
            (record["school_year"], record["grade_level"]): record
            for record in records
        }
        records_by_year = {}
        for record in records:
            records_by_year.setdefault(record["school_year"], []).append(record)
        grade_years = {}
        for record in records:
            grade_years.setdefault(record["grade_level"], set()).add(record["school_year"])

        path_cells = []
        missing_steps = []
        for step in expected_path:
            record = records_by_year_grade.get((step["school_year"], step["grade"]))
            if record and not is_missing_status(record["status"]):
                path_cells.append(
                    {
                        "school_year": step["school_year"],
                        "expected_grade": step["grade"],
                        "status": record["status"],
                        "status_label": humanize_status(record["status"]),
                        "completion_status": get_completion_status(record),
                        "remarks": format_remarks(record["status"], record["remarks"]),
                    }
                )
            else:
                missing_steps.append(step)
                path_cells.append(
                    {
                        "school_year": step["school_year"],
                        "expected_grade": step["grade"],
                        "status": "MISSING",
                        "status_label": humanize_status("MISSING"),
                        "completion_status": "",
                        "remarks": "",
                    }
                )

        has_grade10 = any(
            record["grade_level"] == 10 and is_active_enrollment_status(record["status"])
            for record in records
        )
        expected_grade10_record = records_by_year_grade.get((end_year, 10))
        has_expected_grade10 = bool(
            expected_grade10_record and is_completer_record(expected_grade10_record)
        )
        has_transfer_out = any(record["status"] == "TRANSFER_OUT" for record in records)
        has_pending_transfer = any(record["status"] == "PENDING_TRANSFER_IN" for record in records)
        has_repetition = any(
            len(
                {
                    record["school_year"]
                    for record in records
                    if record["grade_level"] == grade and not is_missing_status(record["status"])
                }
            )
            > 1
            for grade in grade_years
        )
        has_grade10_completer = bool(expected_grade10_record and is_completer_record(expected_grade10_record))
        has_grade10_survivor = bool(expected_grade10_record and is_survival_record(expected_grade10_record))
        has_grade10_pending = bool(
            expected_grade10_record
            and is_active_enrollment_status(expected_grade10_record["status"])
            and get_completion_status(expected_grade10_record) not in {"PASS", "FAIL"}
        )
        on_time = has_expected_grade10 and not missing_steps and not has_transfer_out
        delayed = any(is_completer_record(record) for record in records) and not on_time

        if has_transfer_out:
            result = "TRANSFER_OUT"
            reason = "Transferred out before completing the expected path"
        elif on_time:
            result = "COMPLETED"
            reason = ""
        elif delayed:
            result = "DELAYED_COMPLETED"
            reason = "Reached Grade 10 later than the expected path"
        elif has_grade10_survivor:
            result = "SURVIVED"
            reason = "Reached Grade 10 but marked Fail"
        elif has_grade10_pending:
            result = "GRADE10_PENDING"
            reason = "Grade 10 outcome needs Pass or Fail"
        elif has_repetition:
            result = "REPEATED"
            reason = "Repeated or delayed in one grade level"
        else:
            result = "INCOMPLETE"
            reason = "Missing expected progression record"

        if has_pending_transfer and result not in {"COMPLETED", "DELAYED_COMPLETED"}:
            reason = "Pending transfer-in record needs verification"

        if on_time:
            summary["on_time"] += 1
        if any(is_completer_record(record) for record in records):
            summary["completed"] += 1
        if has_grade10_survivor:
            summary["grade10_enrollment"] += 1
            summary["survived"] += 1
        if has_grade10_completer:
            summary["grade10_completers"] += 1
        if delayed or has_repetition:
            summary["delayed"] += 1
        if has_repetition:
            summary["repeated"] += 1
        if has_transfer_out:
            summary["transfer_out"] += 1
        if result == "INCOMPLETE":
            summary["incomplete"] += 1
        if result in {"TRANSFER_OUT", "REPEATED", "INCOMPLETE", "DELAYED_COMPLETED", "SURVIVED", "GRADE10_PENDING"} or has_pending_transfer:
            summary["for_review"] += 1

        if has_transfer_out:
            transfer_record = next((record for record in records if record["status"] == "TRANSFER_OUT"), records[-1])
            grade = transfer_record["grade_level"]
            breakdown[grade]["transferred_out"] += 1
            breakdown[grade]["for_review"] += 1
        if has_repetition or delayed:
            latest_grade = max(record["grade_level"] for record in records)
            breakdown[latest_grade]["repeated_or_delayed"] += 1
            breakdown[latest_grade]["for_review"] += 1
        if missing_steps and not has_grade10 and not has_transfer_out:
            grade = missing_steps[0]["grade"]
            breakdown[grade]["missing"] += 1
            breakdown[grade]["for_review"] += 1

        if reason:
            latest = records[-1] if records else {"grade_level": start_grade, "school_year": start_year, "remarks": ""}
            review_learners.append(
                {
                    "lrn": lrn,
                    "name": name,
                    "last_grade": latest["grade_level"],
                    "last_year": latest["school_year"],
                    "reason": reason,
                    "remarks": format_remarks(latest.get("status"), latest.get("remarks")) or "-",
                }
            )

        for index, current_step in enumerate(expected_path[1:]):
            previous_step = expected_path[index]
            transition = transition_breakdown[index]
            previous_records = [
                record
                for record in records_by_year.get(previous_step["school_year"], [])
                if not is_missing_status(record["status"])
            ]
            current_records = [
                record
                for record in records_by_year.get(current_step["school_year"], [])
                if not is_missing_status(record["status"])
            ]
            previous_record = records_by_year_grade.get((previous_step["school_year"], previous_step["grade"]))
            current_expected_record = records_by_year_grade.get((current_step["school_year"], current_step["grade"]))

            if previous_record and is_active_enrollment_status(previous_record["status"]):
                transition["previous_enrollment"] += 1
                transition_totals["previous_enrollment"] += 1

                if (
                    current_expected_record
                    and is_active_enrollment_status(current_expected_record["status"])
                    and not is_transfer_in_status(current_expected_record["status"])
                ):
                    transition["retained"] += 1
                    transition_totals["retained"] += 1

            if current_records:
                transition["current_students"] += 1
                transition_totals["current_students"] += 1

                if previous_records and any(
                    current_record["grade_level"] == previous_record_item["grade_level"]
                    for current_record in current_records
                    for previous_record_item in previous_records
                ):
                    transition["repeated"] += 1
                    transition_totals["repeated"] += 1

        rows.append(
            {
                "lrn": lrn,
                "name": name,
                "path": path_cells,
                "result": result,
                "result_label": humanize_status(result),
                "reason": reason,
            }
        )

    current_transition = transition_breakdown[-1] if transition_breakdown else {
        "previous_enrollment": 0,
        "retained": 0,
        "current_students": 0,
        "repeated": 0,
    }
    summary["survival"] = summary["grade10_enrollment"]

    rates = {
        "on_time_completion": round((summary["on_time"] / summary["total"]) * 100, 2) if summary["total"] else 0,
        "overall_completion": round((summary["completed"] / summary["total"]) * 100, 2) if summary["total"] else 0,
        "completion": round((summary["grade10_completers"] / summary["total"]) * 100, 2) if summary["total"] else 0,
        "survival": round((summary["grade10_enrollment"] / summary["total"]) * 100, 2) if summary["total"] else 0,
        "retention": round((current_transition["retained"] / current_transition["previous_enrollment"]) * 100, 2)
        if current_transition["previous_enrollment"]
        else 0,
        "repetition": round((current_transition["repeated"] / current_transition["current_students"]) * 100, 2)
        if current_transition["current_students"]
        else 0,
    }

    for transition in transition_breakdown:
        transition["retention_rate"] = (
            round((transition["retained"] / transition["previous_enrollment"]) * 100, 2)
            if transition["previous_enrollment"]
            else 0
        )
        transition["repetition_rate"] = (
            round((transition["repeated"] / transition["current_students"]) * 100, 2)
            if transition["current_students"]
            else 0
        )

    baseline_step = expected_path[0]
    transition_breakdown = [
        {
            "school_year": baseline_step["school_year"],
            "grade": baseline_step["grade"],
            "previous_school_year": "",
            "previous_grade": "",
            "previous_enrollment": "N/A",
            "retained": "N/A",
            "current_students": summary["total"],
            "repeated": "N/A",
            "retention_rate": "N/A",
            "repetition_rate": "N/A",
            "is_baseline": True,
        }
    ] + transition_breakdown

    return {
        "start_year": start_year,
        "end_year": end_year,
        "start_grade": start_grade,
        "title": f"Grade {start_grade} Entry Cohort Progression Report: {start_year} to {end_year}",
        "expected_path": expected_path,
        "summary": summary,
        "rates": rates,
        "breakdown": list(breakdown.values()),
        "transition_breakdown": transition_breakdown,
        "transition_totals": transition_totals,
        "review_learners": review_learners,
        "rows": rows,
    }
