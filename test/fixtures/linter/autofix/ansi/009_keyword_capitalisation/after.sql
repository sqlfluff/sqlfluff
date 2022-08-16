select
	credits.*,
	min(party.created_datetime) as first_party_created_datetime,
	listagg(distinct party.product_category_code, ', ') as party_product_category_codes,
	listagg(distinct party.product_category_name, ', ') as party_product_category_names,
	listagg(distinct party.party_type_id, ', ') as party_type_ids,
	listagg(distinct party.party_type, ', ') as party_types,
	listagg(distinct party.party_action_id, ', ') as party_action_ids,
	listagg(distinct party.party_action, ', ') as party_actions,
	listagg(distinct party.party_incident_id, ', ') as party_incident_ids,
	listagg(distinct party.incident, ', ') as party_incidents,
	listagg(distinct party.product_party_package_id, ', ') as party_product_party_package_ids,
	listagg(distinct party.product_party_party_type, ', ') as party_product_party_party_types
from (
	select
		created,
		party_transaction_id as big_transaction_id,
		punter_id,
		credit_amount,
		promo_punter_reward_id,
		NULLIF(SUBSTRING(regexp_substr(cr.description,'Ticket ref: [0-9]*'), 13), '') ::INT as ticket_id,
		case when cr.description like 'Requesting Punter: %'
			then left(
				SUBSTRING(regexp_substr(cr.description,'Requesting Punter: [^/]*'), 18),
				length(SUBSTRING(regexp_substr(cr.description,'Requesting Punter: [^/]*'), 18) )-1)
			else null end as punter_name,
		cr.description,
		party_reason_id,
		car.description as reason
	from {{ ref("party_default__party_transaction") }} cr
		join {{ ref("party_default__party_reason") }} car using (party_reason_id)
	)
group by 1,2,3,4,5,6,7,8,9
	union
select
	created,
	mgm_big_transaction_id as big_transaction_id,
	punter_id,
	credit_amount,
	promo_punter_reward_id,
	null as ticket_id,
	null as punter_name,
	null as description,
	null as reason_id,
	'raf' as reason,
	null as first_party_created_datetime,
	null as party_product_category_codes,
	null as party_product_category_names,
	null as party_type_ids,
	null as party_types,
	null as party_action_ids,
	null as party_actions,
	null as party_incident_ids,
	null as party_incidents,
	null as party_product_party_package_ids,
	-- NULL as party_product_party_product_types,
	null as party_product_party_party_types
from {{ ref("party_default__mgm_big_transaction") }}
