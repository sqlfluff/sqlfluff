PROMPT ALTER TABLE CAMPAIGN_GROUPS TO ADD OBJECTIVE_TYPE, DAILY_BUDGET, LIFETIME_BUDGET, WEEKLY_BUDGET, WEEKLY_BUDGET_UPDATE_TIME, OPTIMIZATION_TARGET, COST_TYPE, DYNAMIC_BUDGET_OPT_ENABLED COLUMNS
ALTER TABLE CAMPAIGN_GROUPS ADD (
    OBJECTIVE_TYPE VARCHAR2(50),
    DAILY_BUDGET NUMBER(20,2),
    LIFETIME_BUDGET NUMBER(20,2),
    WEEKLY_BUDGET NUMBER(20,2),
    WEEKLY_BUDGET_UPDATE_TIME TIMESTAMP (6),
    OPTIMIZATION_TARGET VARCHAR2(50),
    COST_TYPE VARCHAR2(20),
    DYNAMIC_BUDGET_OPT_ENABLED NUMBER(1)
);

COMMENT ON COLUMN CAMPAIGN_GROUPS.OBJECTIVE_TYPE IS '<compliance> {"dataType": "NONE"} </compliance> Indicates the objective type for a campaign group';
COMMENT ON COLUMN CAMPAIGN_GROUPS.DAILY_BUDGET IS '<compliance> {"dataType": "NONE"} </compliance> The daily amount to spend across all campaigns under this campaign group, used only if the campaign group is enabled for dynamic budget optimization';
COMMENT ON COLUMN CAMPAIGN_GROUPS.LIFETIME_BUDGET IS '<compliance> {"dataType": "NONE"} </compliance> The lifetime budget amount to spend during the lifetime of the campaign group, which is derived from the runSchedule, used only if the campaign group is enabled for dynamic budget optimization';
COMMENT ON COLUMN CAMPAIGN_GROUPS.WEEKLY_BUDGET IS '<compliance> {"dataType": "NONE"} </compliance> The weekly delivery goal and charging limit of a campaign group, used only if the campaign group is enabled for dynamic budget optimization';
COMMENT ON COLUMN CAMPAIGN_GROUPS.WEEKLY_BUDGET_UPDATE_TIME IS '<compliance> {"dataType": "NONE"} </compliance> Indicates the last timestamp the weekly budget was updated, used only if the campaign group is enabled for dynamic budget optimization';
COMMENT ON COLUMN CAMPAIGN_GROUPS.OPTIMIZATION_TARGET IS '<compliance> {"dataType": "NONE"} </compliance> Indicates how this campaign group is optimized, used only if the campaign group is enabled for dynamic budget optimization';
COMMENT ON COLUMN CAMPAIGN_GROUPS.COST_TYPE IS '<compliance> {"dataType": "NONE"} </compliance> Indicates whether this campaign group is charged per impression, per click, or other model, used only if the campaign group is enabled for dynamic budget optimization';
COMMENT ON COLUMN CAMPAIGN_GROUPS.DYNAMIC_BUDGET_OPT_ENABLED IS '<compliance> {"dataType": "NONE"} </compliance> Indicates whether this campaign group is enabled for Dynamic Budget Optimization, which dynamically allocates budget across campaigns';

SHOW ERRORS;