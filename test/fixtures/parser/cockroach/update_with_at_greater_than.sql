update t1 set a = jsonb_set(a, '{nata,pastryStructureEligibility,0,pastryIncluded,0}'::string[], '"PUF"') where a @> '{"nata": {"pastryStructureEligibility": [{"pastryIncluded": ["PF"]}]}}';
