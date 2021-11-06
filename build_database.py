import httpx
import sqlite_utils


def fetch_data():
    return httpx.get(
        "https://raw.githubusercontent.com/salesforce/policy_sentry/master/policy_sentry/shared/data/iam-definition.json"
    ).json()


def build(data, filepath):
    db = sqlite_utils.Database(filepath)
    for service in data.values():
        privileges = service.pop("privileges")
        resources = service.pop("resources")
        conditions = service.pop("conditions")
        db["services"].insert(service, alter=True, pk="prefix")
        # resources
        resource_items = list(resources.values())
        for resource_item in resource_items:
            resource_item["service"] = service["prefix"]
        db["resources"].insert_all(
            resource_items,
            foreign_keys=(("service", "services", "prefix"),),
            column_order=("service", "resource"),
        )
        # privileges
        privilege_items = list(privileges.values())
        for privilege_item in privilege_items:
            privilege_item["service"] = service["prefix"]
        db["privileges"].insert_all(
            privilege_items,
            foreign_keys=(("service", "services", "prefix"),),
            column_order=("service", "privilege"),
        )
        # conditions
        condition_items = list(conditions.values())
        for condition_item in condition_items:
            condition_item["service"] = service["prefix"]
        db["conditions"].insert_all(
            condition_items,
            foreign_keys=(("service", "services", "prefix"),),
            column_order=("service", "condition"),
        )


if __name__ == "__main__":
    build(fetch_data(), filepath="iam.db")
