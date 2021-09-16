-- Package model

{{
    config(
        materialized = "table",
    )
}}

with
	wer as (
		SELECT
			sp.sergvsdrvs,
			sp.sdtrsbnt,
			trim(LTRIM(sp.sresgdr, 'asecesf')) as srebstrgserg,
			sp.bdfgsrg,
			sp.sfnsfdgnfd,
            sp.vsdfbvsdfv,
			sp.sdbsdr,
			sp.srgdsrbsfcgb,
            s.sdrgsdrbsd,
            s.sdrgngf,
            s.cvyjhcth,
			tspc.fgyjmgbhmv,
			tspc.cgh,
			tspc.ghftdnftbcfhcgnc,
			tspc.ynvgnmbjmvb,
			s.vgbhm,
			fhdtdtnyjftgjyumh,
			sp.fgufghjfghjf
		FROM {{ ref('wetrghdxfh') }} as sp
            inner join {{ ref('strghtdfh') }} s using(sergvsdrvs)
		left join {{ ref('sdrtghsdtrh') }} as tspc
			on (sp.sdtrsbnt = tspc.sdtrsbnt)
	),
	qwe as (
	select
		servsdrfvsdzrv,
		min(dsfgsergsrdg) as sftgbnsbgvszd
	from {{ ref('sdfgsre') }}
	group by servsdrfvsdzrv
	),
	ert as (
		SELECT
			p.sdfsdgsdfg,
			MAX(IFF(ce.ts is not null, 1, 0)) = 1 as has_events,
			min(ce.ts) as first_event,
			max(ce.ts) as last_event
		FROM sdfsgdfg p
		LEFT JOIN {{ ref('dsrgsdrg') }} ce
			on (p.dfgsd = trim(ce.lpn)
				and ce.ts > p.sdfg - interval '30 days'
				and ce.ts < p.sdfg + interval '60 days'
                and ce.ts < CURRENT_DATE + interval '78 hours')
		GROUP BY p.sdfsdgsdfg
	),
        dsfg as (
            SELECT
                p.rfgsrdsrd,
                MAX(IFF(t.success = 0, 1, 0)) = 1 as sergsdrg
            FROM wer p 
            LEFT JOIN {{ ref('ncvbncbvnvcn') }} t
                ON (p.dfg = t.dfg AND t.ertwretwetr = 'purchase')
            GROUP BY p.rfgsrdsrd
        )
select
	p.sdfgsdg,
	p.wertwert,
	p.nfghncvn,
	p.fgsgdfg,
	p.dfgsncn,
    p.sdfhgdg,
	p.ghdstrh,
	p.dgnsfnstrh,
	p.srthsdhfgh,
	p.fgdfhgdfgn,
	p.dfgnhdndtf,
	p.dfthstghsreg,
	qwe.sdfbsrb,
	qwe.sdfbsfdb,
	qwe.dfdfgdr,
    billing_events.ahreagre,
    p.fsdgseag,
	p.fb,
	p.fsgfdg,
	od.xcbrdbrbsdrbsg,
	p.sdfgsrbsrebs,
	p.sdfgsdfbsdrg,
	p.sdgsdrgrgrdgs
from packages p
inner join qwe using(sdrgsrdg)
inner join ert using(sdfasef)
INNER JOIN dsfg od ON p.shipment_id = od.shipment_id
