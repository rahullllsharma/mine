import json

jsb_file_path = "tests/unit/jsb_migration/jsb.json"
test_user_id = "test_id"
test_tenant_id = "test_tenant_id"


def update_jsb_contents(jsbs: list[dict]) -> list[dict]:
    jsbs_data = jsbs
    for item in jsbs_data:
        contents = item["contents"]
        completions = contents.get("completions", []) or []
        if completions:
            for i in contents["completions"]:
                i["completed_by_id"] = str(test_user_id)
            updated_contents = contents
            item["contents"] = updated_contents
        item["tenant_id"] = test_tenant_id
    return jsbs_data


def test_jsb_migration() -> None:
    jsb_data = []
    with open(jsb_file_path, "r") as file:
        jsb_data = json.load(file)
    jsbs_data_updated = update_jsb_contents(jsbs=jsb_data)
    for item in jsbs_data_updated:
        assert item["tenant_id"] == test_tenant_id
        contents = item["contents"]
        completions = contents.get("completions", []) or []
        if completions:
            for item in completions:
                assert item["completed_by_id"] == test_user_id
