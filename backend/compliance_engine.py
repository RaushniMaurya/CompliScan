import json

def load_rules(rules_path="rules.json"):
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_compliance(extracted_fields, rules_path="rules.json"):
    """
    Compares extracted label fields against the mandatory declarations
    from the Legal Metrology (Packaged Commodities) Rules, 2011.
    Returns an overall status + a per-field breakdown.
    """
    rules = load_rules(rules_path)
    results = []
    missing_required_count = 0

    for decl in rules["declarations"]:
        field = decl["field"]
        found = extracted_fields.get(field)

        if found:
            status = "PASS"
        elif decl["required"]:
            status = "POTENTIAL_VIOLATION"
            missing_required_count += 1
        else:
            status = "NOT_APPLICABLE"

        results.append({
            "field": field,
            "label": decl["label"],
            "required": decl["required"],
            "detected_value": found if found else None,
            "status": status,
            "rule_reference": decl["notes"]
        })

    if missing_required_count == 0:
        overall = "COMPLIANT"
    elif missing_required_count <= 2:
        overall = "NEEDS_VERIFICATION"
    else:
        overall = "POTENTIAL_NON_COMPLIANCE"

    return {
        "overall_status": overall,
        "missing_required_count": missing_required_count,
        "details": results
    }


if __name__ == "__main__":
    # Quick test using fields we already extracted from the Kellogg's image
    sample_extracted = {
        "mrp": "10.00",
        "net_quantity": "30 g",
        "manufacturer": "KELLOGG INDIA PVT. LTD.",
        "consumer_care": "1800-22-3500"
    }

    report = check_compliance(sample_extracted)

    print("===== COMPLIANCE REPORT =====")
    print(f"Overall Status: {report['overall_status']}")
    print(f"Missing Required Declarations: {report['missing_required_count']}\n")

    for item in report["details"]:
        mark = "✅" if item["status"] == "PASS" else ("⚠️" if item["status"] == "NOT_APPLICABLE" else "❌")
        print(f"{mark} {item['label']} ({item['field']})")
        print(f"    Status: {item['status']}")
        print(f"    Detected: {item['detected_value']}")
        print(f"    Rule: {item['rule_reference']}\n")