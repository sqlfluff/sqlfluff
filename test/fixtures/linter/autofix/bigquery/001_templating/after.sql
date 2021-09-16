select *
from  `{{project}}.{{dataset}}.user_labels_with_probs`
where prob_max >= {{label_prob_threshold}}
    --- only focus on 3 segments
    and label_str not in ('marketing_maven', 'growth_services')
