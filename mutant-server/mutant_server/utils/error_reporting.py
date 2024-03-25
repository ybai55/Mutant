from mutant_server.utils.config.settings import get_settings

import sentry_sdk
from sentry_sdk.client import Client
from sentry_sdk import configure_scope
from posthog.sentry.posthog_integration import PostHogIntegration

PostHogIntegration.organization = "mutant"
sample_rate = 1.0
if get_settings().environment == "production":
    sample_rate = 0.1


def init_error_reporting():
    mutant_client = Client(
        dsn="https://c23d980ea90a8c44e0c19772a5b600d8@o4506970231996416.ingest.us.sentry.io/4506970240712704"
    )
    if get_settings().user_sentry_dsn:
        user_client = Client(dsn=get_settings().user_sentry_dsn)

    def send_event(event):
        mutant_client.capture_event(event)
        if get_settings().user_sentry_dsn:
            user_client.capture_event(event)

    sentry_sdk.init(
        transport=send_event,
        traces_sample_rate=sample_rate,
        integrations=[PostHogIntegration()],
        environment=get_settings().environment,
    )
    with configure_scope() as scope:
        scope.set_tag("posthog_distinct_id", get_settings().telemetry_anonymized_uuid)
