SELECT
COUNT(1) AS campaign_count,
state_user_v_peer_open
,business_type

-- The following is the slope of the regression line. Note that CORR (which is the Pearson's correlation
--  coefficient is symmetric in its arguments, but since STDDEV_POP(open_rate_su) appears in the
--  numerator this is the slope of the regression line considering STDDEV_POP(open_rate_su) to be
--  the "y variable" and uses_small_subject_line to be the "x variable" in terms of the regression line.
,SAFE_DIVIDE(SAFE_MULTIPLY(CORR(open_rate_su, uses_small_subject_line), STDDEV_POP(open_rate_su)), STDDEV_POP(uses_small_subject_line))

FROM
global_actions_states
