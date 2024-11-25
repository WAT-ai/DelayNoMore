from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    load_assets_from_modules,
    EnvVar
)

from . import assets
from .resources import DataGeneratorResource

all_assets = load_assets_from_modules([assets])

# Addition: a ScheduleDefinition targeting all assets and a cron schedule of how frequently to run it
hackernews_schedule = ScheduleDefinition(
    name="hackernews_schedule",
    target=AssetSelection.all(),
    cron_schedule="0 * * * *",  # every hour
)

datagen = DataGeneratorResource(
    num_days=EnvVar.int("HACKERNEWS_NUM_DAYS_WINDOW"),
)

defs = Definitions(
    assets=all_assets,
    schedules=[hackernews_schedule],
    resources={
        "hackernews_api": datagen,  # Add the newly-made resource here
    },
)