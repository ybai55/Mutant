from mutant_server.utils.config.settings import get_settings

import sentry_sdk
from sentry_sdk.client import Client
from sentry_sdk import configure_scope
from posthog.sentry.posthog_integration import PostHogIntegration

PostHogIntegration.organization = "mutant"
sample_rate = 1.0
if get_settings().environment == "production":
    sample_rate = 0.1


def strip_sensitive_data(event, hint):
    if "server_name" in event:
        del event["server_name"]
        return event


def init_error_reporting():

    sentry_sdk.init(
        dsn="https://c23d980ea90a8c44e0c19772a5b600d8@o4506970231996416.ingest.us.sentry.io/4506970240712704",
        traces_sample_rate=sample_rate,
        integrations=[PostHogIntegration()],
        environment=get_settings().environment,
        before_send=strip_sensitive_data,
    )
    with configure_scope() as scope:
        scope.set_tag("posthog_distinct_id", get_settings().telemetry_anonymized_uuid)
