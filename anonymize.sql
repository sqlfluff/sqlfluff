-- /*Select list of users to choose from for training*/ 
drop table if exists db_2.table_1_MASTER;
CREATE TABLE db_2.table_1_MASTER AS
SELECT SEG.*,dim.col_208,dim.col_589,dim.col_407,dim.col_180,
dim.col_154,dim.col_585
FROM db_3.table_36 AS SEG
JOIN db_3.table_30 DIM ON DIM.col_149 = SEG.col_149
JOIN db_1.table_19 CNT ON SEG.col_381 = CNT.col_381
WHERE 1=1
AND CURRENT_DATE BETWEEN SEG.col_119 AND SEG.col_555  
AND CNT.col_319 in ('US');

select * from db_2.table_1_MASTER;

-- describe db_3.table_30;

-- Run this score 12 times to get data for all 12 months
-- Sample 1m users to score
drop table if exists db_2.table_1;
create TABLE db_2.table_1 as 
select distinct col_149 from db_2.table_1_MASTER order by rand() limit 3000000;

--set candidatedate=2020-11-01;

drop table if EXISTS db_2.table_14;
create table db_2.table_14 as 
select
	USR.col_149
	,'${candidatedate}' as col_267                                                                               
	-- BIDS
	,COALESCE(avg(col_197),0) as col_60
	,COALESCE(max(col_197),0) as col_47
	,COALESCE(min(col_197),0) as col_95
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_197 else 0 end) as col_126
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_197 else 0 end) as t_1w_2w_col_197
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_197 else 0 end) as t_3w_4w_col_197
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_197 else 0 end) as t_4w_col_197
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_197 else 0 end) as t_1m_2m_col_197
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_197 else 0 end) as t_2m_3m_col_197
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_197 else 0 end) as col_125
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_197 else 0 end) as t_6m_1y_col_197
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_197 else 0 end) as col_136
	,coalesce((col_126/col_60),0) as col_608
	,coalesce((t_1w_2w_col_197/col_60),0) as col_460
	,coalesce((t_3w_4w_col_197/col_60),0) as col_114
	,coalesce((t_4w_col_197/col_60),0) as col_366
	,coalesce((t_1m_2m_col_197/col_60),0) as col_348
	,coalesce((t_2m_3m_col_197/col_60),0) as col_107
	,coalesce((col_126/col_47),0) as col_5
	,coalesce((t_1w_2w_col_197/col_47),0) as t_1w_2w_col_408d_index
	,coalesce((t_3w_4w_col_197/col_47),0) as col_360
	,coalesce((t_4w_col_197/col_47),0) as col_236
	,coalesce((t_1m_2m_col_197/col_47),0) as col_135
	,coalesce((t_2m_3m_col_197/col_47),0) as col_165
	,coalesce((col_126/col_95),0) as t_1w_col_413d_index
	,coalesce((t_1w_2w_col_197/col_95),0) as t_1w_2w_col_413d_index
	,coalesce((t_3w_4w_col_197/col_95),0) as col_398
	,coalesce((t_4w_col_197/col_95),0) as col_306
	,coalesce((t_1m_2m_col_197/col_95),0) as col_79
	,coalesce((t_2m_3m_col_197/col_95),0) as t_2m_3m_col_413d_index
	-- WATCHES
	,COALESCE(avg(col_362),0) as col_53
	,COALESCE(max(col_362),0) as col_240
	,COALESCE(min(col_362),0) as min_col_362
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_362 else 0 end) as col_344
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_362 else 0 end) as t_1w_2w_col_362
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_362 else 0 end) as t_3w_4w_col_362
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_362 else 0 end) as col_283
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_362 else 0 end) as col_241
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_362 else 0 end) as col_52
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_362 else 0 end) as t_3m_6m_col_362
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_362 else 0 end) as col_82
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_362 else 0 end) as col_8
	,coalesce((col_344/col_53),0) as col_473
	,coalesce((t_1w_2w_col_362/col_53),0) as col_525
	,coalesce((t_3w_4w_col_362/col_53),0) as col_588
	,coalesce((col_283/col_53),0) as col_216
	,coalesce((col_241/col_53),0) as col_502
	,coalesce((col_52/col_53),0) as col_73
	,coalesce((col_344/col_240),0) as col_402
	,coalesce((t_1w_2w_col_362/col_240),0) as col_229
	,coalesce((t_3w_4w_col_362/col_240),0) as col_263
	,coalesce((col_283/col_240),0) as col_207
	,coalesce((col_241/col_240),0) as col_529
	,coalesce((col_52/col_240),0) as col_237
	,coalesce((col_344/min_col_362),0) as col_590
	,coalesce((t_1w_2w_col_362/min_col_362),0) as col_507
	,coalesce((t_3w_4w_col_362/min_col_362),0) as col_264
	,coalesce((col_283/min_col_362),0) as col_372
	,coalesce((col_241/min_col_362),0) as col_296
	,coalesce((col_52/min_col_362),0) as col_38
	-- OFFERS
	,COALESCE(avg(col_611),0) as col_521
	,COALESCE(max(col_611),0) as col_562
	,COALESCE(min(col_611),0) as col_330
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_611 else 0 end) as col_383
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_611 else 0 end) as col_288
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_611 else 0 end) as col_598
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_611 else 0 end) as col_178
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_611 else 0 end) as col_59
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_611 else 0 end) as col_93
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_611 else 0 end) as col_20
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_611 else 0 end) as col_485
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_611 else 0 end) as col_387
	,coalesce((col_383/col_521),0) as col_597
	,coalesce((col_288/col_521),0) as col_106
	,coalesce((col_598/col_521),0) as col_108
	,coalesce((col_178/col_521),0) as col_426
	,coalesce((col_59/col_521),0) as col_88
	,coalesce((col_93/col_521),0) as col_97
	,coalesce((col_383/col_562),0) as col_404
	,coalesce((col_288/col_562),0) as col_199
	,coalesce((col_598/col_562),0) as col_347
	,coalesce((col_178/col_562),0) as col_401
	,coalesce((col_59/col_562),0) as col_515
	,coalesce((col_93/col_562),0) as col_434
	,coalesce((col_383/col_330),0) as col_466
	,coalesce((col_288/col_330),0) as col_395
	,coalesce((col_598/col_330),0) as col_54
	,coalesce((col_178/col_330),0) as col_392
	,coalesce((col_59/col_330),0) as col_225
	,coalesce((col_93/col_330),0) as col_537
	-- ASQ
	,COALESCE(avg(col_158),0) as avg_col_158
	,COALESCE(max(col_158),0) as max_col_158
	,COALESCE(min(col_158),0) as min_col_158
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_158 else 0 end) as t_1w_col_158
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_158 else 0 end) as t_1w_2w_col_158
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_158 else 0 end) as t_3w_4w_col_158
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_158 else 0 end) as col_2
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_158 else 0 end) as col_50
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_158 else 0 end) as col_121
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_158 else 0 end) as t_3m_6m_col_158
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_158 else 0 end) as t_6m_1y_col_158
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_158 else 0 end) as t_1y_2y_col_158
	,coalesce((t_1w_col_158/avg_col_158),0) as col_201
	,coalesce((t_1w_2w_col_158/avg_col_158),0) as col_441
	,coalesce((t_3w_4w_col_158/avg_col_158),0) as col_430
	,coalesce((col_2/avg_col_158),0) as col_541
	,coalesce((col_50/avg_col_158),0) as col_265
	,coalesce((col_121/avg_col_158),0) as col_220
	,coalesce((t_1w_col_158/max_col_158),0) as col_222
	,coalesce((t_1w_2w_col_158/max_col_158),0) as col_271
	,coalesce((t_3w_4w_col_158/max_col_158),0) as col_614
	,coalesce((col_2/max_col_158),0) as col_66
	,coalesce((col_50/max_col_158),0) as col_469
	,coalesce((col_121/max_col_158),0) as col_516
	,coalesce((t_1w_col_158/min_col_158),0) as col_24
	,coalesce((t_1w_2w_col_158/min_col_158),0) as col_477
	,coalesce((t_3w_4w_col_158/min_col_158),0) as col_325
	,coalesce((col_2/min_col_158),0) as col_137
	,coalesce((col_50/min_col_158),0) as col_99
	,coalesce((col_121/min_col_158),0) as col_261
	-- ATC
	,COALESCE(avg(col_422),0) as col_481
	,COALESCE(max(col_422),0) as col_498
	,COALESCE(min(col_422),0) as col_143
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_422 else 0 end) as col_213
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_422 else 0 end) as col_122
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_422 else 0 end) as col_31
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_422 else 0 end) as col_327
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_422 else 0 end) as col_268
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_422 else 0 end) as col_552
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_422 else 0 end) as col_400
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_422 else 0 end) as col_578
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_422 else 0 end) as col_382
	,coalesce((col_213/col_481),0) as col_35
	,coalesce((col_122/col_481),0) as col_596
	,coalesce((col_31/col_481),0) as col_127
	,coalesce((col_327/col_481),0) as col_61
	,coalesce((col_268/col_481),0) as col_594
	,coalesce((col_552/col_481),0) as col_193
	,coalesce((col_213/col_498),0) as col_335
	,coalesce((col_122/col_498),0) as col_463
	,coalesce((col_31/col_498),0) as col_544
	,coalesce((col_327/col_498),0) as col_160
	,coalesce((col_268/col_498),0) as col_494
	,coalesce((col_552/col_498),0) as col_573
	,coalesce((col_213/col_143),0) as col_527
	,coalesce((col_122/col_143),0) as col_218
	,coalesce((col_31/col_143),0) as col_43
	,coalesce((col_327/col_143),0) as col_388
	,coalesce((col_268/col_143),0) as col_62
	,coalesce((col_552/col_143),0) as col_258
	-- BIN
	,COALESCE(avg(col_287),0) as col_191
	,COALESCE(max(col_287),0) as col_408n_cnt
	,COALESCE(min(col_287),0) as col_234
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_287 else 0 end ) as col_483
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_287 else 0 end ) as col_508
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_287 else 0 end ) as col_23
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_287 else 0 end ) as col_272
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_287 else 0 end ) as col_257
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_287 else 0 end ) as col_204
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_287 else 0 end ) as col_505
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_287 else 0 end ) as col_16
	,SUM( CASE WHEN BIN_SOLD_IND=1 AND col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_287 else 0 end ) as col_447
	,coalesce((col_483/col_191),0) as col_391
	,coalesce((col_508/col_191),0) as col_18
	,coalesce((col_23/col_191),0) as col_577
	,coalesce((col_272/col_191),0) as col_520
	,coalesce((col_257/col_191),0) as col_75
	,coalesce((col_204/col_191),0) as col_58
	,coalesce((col_483/col_408n_cnt),0) as t_1w_col_408n_index
	,coalesce((col_508/col_408n_cnt),0) as t_1w_2w_col_408n_index
	,coalesce((col_23/col_408n_cnt),0) as t_3w_4w_col_408n_index
	,coalesce((col_272/col_408n_cnt),0) as t_4w_col_408n_index
	,coalesce((col_257/col_408n_cnt),0) as t_1m_2m_col_408n_index
	,coalesce((col_204/col_408n_cnt),0) as t_2m_3m_col_408n_index
	,coalesce((col_483/col_234),0) as col_76
	,coalesce((col_508/col_234),0) as col_27
	,coalesce((col_23/col_234),0) as col_405
	,coalesce((col_272/col_234),0) as t_4w_col_413n_index
	,coalesce((col_257/col_234),0) as t_1m_2m_col_413n_index
	,coalesce((col_204/col_234),0) as col_297
from
	db_2.table_1 USR
left join
	db_1.table_28 SD
	on USR.col_149 = SD.col_149
	and SD.col_170 >= '${candidatedate}' - interval '910' day
group by 1,2
;

select * from db_2.table_14 where col_382>0;


drop table if exists db_2.table_23;
create table db_2.table_23 as 
select
	USR.col_149
	,'${candidatedate}' as col_267
	-- VIEW ITEM
	,COALESCE(avg(col_179),0) as col_290
	,COALESCE(max(col_179),0) as col_183
	,COALESCE(min(col_179),0) as col_147
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_179 else 0 end) as col_156
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_179 else 0 end) as col_386
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_179 else 0 end) as col_530
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_179 else 0 end) as col_14
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_179 else 0 end) as col_576
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_179 else 0 end) as col_194
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_179 else 0 end) as col_412
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_179 else 0 end) as col_253
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_179 else 0 end) as col_609
	,coalesce((col_156/col_290),0) as col_595
	,coalesce((col_386/col_290),0) as col_567
	,coalesce((col_530/col_290),0) as col_439
	,coalesce((col_14/col_290),0) as col_380
	,coalesce((col_576/col_290),0) as col_517
	,coalesce((col_194/col_290),0) as col_100
	,coalesce((col_156/col_183),0) as col_410
	,coalesce((col_386/col_183),0) as col_414
	,coalesce((col_530/col_183),0) as col_417
	,coalesce((col_14/col_183),0) as col_454
	,coalesce((col_576/col_183),0) as col_350
	,coalesce((col_194/col_183),0) as col_432
	,coalesce((col_156/col_147),0) as col_354
	,coalesce((col_386/col_147),0) as col_56
	,coalesce((col_530/col_147),0) as col_64
	,coalesce((col_14/col_147),0) as col_605
	,coalesce((col_576/col_147),0) as col_176
	,coalesce((col_194/col_147),0) as col_192
	-- SEARCHES
	,COALESCE(avg(col_246),0) as col_86
	,COALESCE(max(col_246),0) as col_307
	,COALESCE(min(col_246),0) as col_438
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_246 else 0 end) as col_560
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_246 else 0 end) as col_315
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_246 else 0 end) as col_338
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_246 else 0 end) as col_571
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_246 else 0 end) as col_299
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_246 else 0 end) as col_580
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_246 else 0 end) as col_270
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_246 else 0 end) as col_260
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_246 else 0 end) as col_600
	,coalesce((col_560/col_86),0) as col_256
	,coalesce((col_315/col_86),0) as col_80
	,coalesce((col_338/col_86),0) as col_251
	,coalesce((col_571/col_86),0) as col_617
	,coalesce((col_299/col_86),0) as col_345
	,coalesce((col_580/col_86),0) as col_496
	,coalesce((col_560/col_307),0) as col_105
	,coalesce((col_315/col_307),0) as col_455
	,coalesce((col_338/col_307),0) as col_118
	,coalesce((col_571/col_307),0) as col_370
	,coalesce((col_299/col_307),0) as col_28
	,coalesce((col_580/col_307),0) as col_13
	,coalesce((col_560/col_438),0) as col_212
	,coalesce((col_315/col_438),0) as col_189
	,coalesce((col_338/col_438),0) as col_198
	,coalesce((col_571/col_438),0) as col_63
	,coalesce((col_299/col_438),0) as col_423
	,coalesce((col_580/col_438),0) as col_443
	-- SESSION DURATION
	,COALESCE(avg(col_602),0) as col_9
	,COALESCE(max(col_602),0) as col_363
	,COALESCE(min(col_602),0) as col_312
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_602 else 0 end) as col_471
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_602 else 0 end) as col_300
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_602 else 0 end) as col_215
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_602 else 0 end) as col_96
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_602 else 0 end) as col_458
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_602 else 0 end) as col_277
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_602 else 0 end) as col_141
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_602 else 0 end) as col_355
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_602 else 0 end) as col_48
	,coalesce((col_471/col_9),0) as col_394
	,coalesce((col_300/col_9),0) as col_166
	,coalesce((col_215/col_9),0) as col_233
	,coalesce((col_96/col_9),0) as col_174
	,coalesce((col_458/col_9),0) as col_490
	,coalesce((col_277/col_9),0) as col_151
	,coalesce((col_471/col_363),0) as col_187
	,coalesce((col_300/col_363),0) as col_532
	,coalesce((col_215/col_363),0) as col_308
	,coalesce((col_96/col_363),0) as col_433
	,coalesce((col_458/col_363),0) as col_132
	,coalesce((col_277/col_363),0) as col_572
	,coalesce((col_471/col_312),0) as col_311
	,coalesce((col_300/col_312),0) as col_266
	,coalesce((col_215/col_312),0) as col_371
	,coalesce((col_96/col_312),0) as col_30
	,coalesce((col_458/col_312),0) as col_556
	,coalesce((col_277/col_312),0) as col_181
	-- VISIT COUNT
	,COALESCE(avg(col_171),0) as avg_col_171
	,COALESCE(max(col_171),0) as max_col_171
	,COALESCE(min(col_171),0) as min_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_171 else 0 end) as t_1w_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_171 else 0 end) as col_33
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_171 else 0 end) as t_3w_4w_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_171 else 0 end) as t_4w_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_171 else 0 end) as t_1m_2m_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_171 else 0 end) as t_2m_3m_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_171 else 0 end) as t_3m_6m_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_171 else 0 end) as t_6m_1y_col_171
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_171 else 0 end) as col_57
	,coalesce((t_1w_col_171/avg_col_171),0) as col_431
	,coalesce((col_33/avg_col_171),0) as col_510
	,coalesce((t_3w_4w_col_171/avg_col_171),0) as col_164
	,coalesce((t_4w_col_171/avg_col_171),0) as col_474
	,coalesce((t_1m_2m_col_171/avg_col_171),0) as col_409
	,coalesce((t_2m_3m_col_171/avg_col_171),0) as col_513
	,coalesce((t_1w_col_171/max_col_171),0) as col_34
	,coalesce((col_33/max_col_171),0) as col_406
	,coalesce((t_3w_4w_col_171/max_col_171),0) as col_3
	,coalesce((t_4w_col_171/max_col_171),0) as col_184
	,coalesce((t_1m_2m_col_171/max_col_171),0) as col_451
	,coalesce((t_2m_3m_col_171/max_col_171),0) as col_470
	,coalesce((t_1w_col_171/min_col_171),0) as col_284
	,coalesce((col_33/min_col_171),0) as col_461
	,coalesce((t_3w_4w_col_171/min_col_171),0) as col_172
	,coalesce((t_4w_col_171/min_col_171),0) as col_549
	,coalesce((t_1m_2m_col_171/min_col_171),0) as col_581
	,coalesce((t_2m_3m_col_171/min_col_171),0) as col_242
	-- VALID PAGE CNT
	,COALESCE(avg(col_511),0) as col_214
	,COALESCE(max(col_511),0) as col_259
	,COALESCE(min(col_511),0) as col_351
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_511 else 0 end) as col_403
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_511 else 0 end) as col_245
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_511 else 0 end) as col_280
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_511 else 0 end) as col_109
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_511 else 0 end) as col_457
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_511 else 0 end) as col_356
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_511 else 0 end) as col_226
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_511 else 0 end) as col_29
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_511 else 0 end) as col_71
	,coalesce((col_403/col_214),0) as col_450
	,coalesce((col_245/col_214),0) as col_228
	,coalesce((col_280/col_214),0) as col_491
	,coalesce((col_109/col_214),0) as col_415
	,coalesce((col_457/col_214),0) as col_209
	,coalesce((col_356/col_214),0) as col_478
	,coalesce((col_403/col_259),0) as col_262
	,coalesce((col_245/col_259),0) as col_563
	,coalesce((col_280/col_259),0) as col_506
	,coalesce((col_109/col_259),0) as col_323
	,coalesce((col_457/col_259),0) as col_167
	,coalesce((col_356/col_259),0) as col_65
	,coalesce((col_403/col_351),0) as col_104
	,coalesce((col_245/col_351),0) as col_486
	,coalesce((col_280/col_351),0) as col_44
	,coalesce((col_109/col_351),0) as col_238
	,coalesce((col_457/col_351),0) as col_169
	,coalesce((col_356/col_351),0) as col_558
	-- HOMEPAGE PAGE CNT
	,COALESCE(avg(col_522),0) as avg_col_522
	,COALESCE(max(col_522),0) as col_255
	,COALESCE(min(col_522),0) as min_col_522
	,sum(case when col_170 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_522 else 0 end) as col_148
	,sum(case when col_170 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_522 else 0 end) as t_1w_2w_col_522
	,sum(case when col_170 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_522 else 0 end) as col_294
	,sum(case when col_170 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_522 else 0 end) as t_4w_col_522
	,sum(case when col_170 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_522 else 0 end) as t_1m_2m_col_522
	,sum(case when col_170 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_522 else 0 end) as t_2m_3m_col_522
	,sum(case when col_170 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_522 else 0 end) as col_293
	,sum(case when col_170 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_522 else 0 end) as t_6m_1y_col_522
	,sum(case when col_170 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_522 else 0 end) as col_92
	,coalesce((col_148/avg_col_522),0) as col_465
	,coalesce((t_1w_2w_col_522/avg_col_522),0) as col_326
	,coalesce((col_294/avg_col_522),0) as col_85
	,coalesce((t_4w_col_522/avg_col_522),0) as col_45
	,coalesce((t_1m_2m_col_522/avg_col_522),0) as col_68
	,coalesce((t_2m_3m_col_522/avg_col_522),0) as col_115
	,coalesce((col_148/col_255),0) as col_196
	,coalesce((t_1w_2w_col_522/col_255),0) as col_369
	,coalesce((col_294/col_255),0) as col_145
	,coalesce((t_4w_col_522/col_255),0) as col_289
	,coalesce((t_1m_2m_col_522/col_255),0) as col_81
	,coalesce((t_2m_3m_col_522/col_255),0) as col_587
	,coalesce((col_148/min_col_522),0) as col_331
	,coalesce((t_1w_2w_col_522/min_col_522),0) as col_539
	,coalesce((col_294/min_col_522),0) as col_336
	,coalesce((t_4w_col_522/min_col_522),0) as col_157
	,coalesce((t_1m_2m_col_522/min_col_522),0) as col_337
	,coalesce((t_2m_3m_col_522/min_col_522),0) as col_250
from
	db_2.table_1 USR
left join
	db_1.table_18 SD
	on USR.col_149 = SD.col_149
	and SD.col_170 >= '${candidatedate}' - interval '910' day
group by 1,2
;

-- describe db_1.table_18;

-- Days between view item 
drop table if exists db_2.table_37;
create table db_2.table_37 AS 
SELECT
USR.col_149,
col_170,
coalesce(col_179,0) as col_179,
COALESCE(col_246,0) as col_246,
coalesce(col_602,0) as col_602 ,
COALESCE(col_171,0) as col_171,
coalesce(col_511,0) as col_511,
coalesce(col_522,0) as col_522
from
db_2.table_1 USR
left join db_1.table_18 SD 
on USR.col_149 = SD.col_149
AND col_170 BETWEEN '${candidatedate}' - interval '730' day AND  '${candidatedate}';

drop table if exists db_2.table_25;
create table db_2.table_25 AS
SELECT
col_149,
AVG(DATEDIFF(to_date(col_170),to_date(col_87))) as col_476
FROM
(SELECT 
col_149, 
col_170, 
LAG(col_170,1) OVER (PARTITION BY col_149 ORDER BY col_170) AS col_87
FROM db_2.table_37
where col_179 <> 0 ) AS LAGGED
GROUP BY col_149
;

drop table if exists db_2.table_34;
create table db_2.table_34 AS
SELECT
col_149,
AVG(DATEDIFF(to_date(col_170),to_date(col_87))) as col_476
FROM
(SELECT 
col_149, 
col_170, 
LAG(col_170,1) OVER (PARTITION BY col_149 ORDER BY col_170) AS col_87
FROM db_2.table_37
where col_246 <> 0 ) AS LAGGED
GROUP BY col_149
;

drop table if exists db_2.table_38;
create table db_2.table_38 AS
SELECT
col_149,
AVG(DATEDIFF(to_date(col_170),to_date(col_87))) as col_476
FROM
(SELECT 
col_149, 
col_170, 
LAG(col_170,1) OVER (PARTITION BY col_149 ORDER BY col_170) AS col_87
FROM db_2.table_37
where col_602 <> 0 ) AS LAGGED
GROUP BY col_149
;

drop table if exists db_2.table_13;
create table db_2.table_13 AS
SELECT
col_149,
AVG(DATEDIFF(to_date(col_170),to_date(col_87))) as col_476
FROM
(SELECT 
col_149, 
col_170, 
LAG(col_170,1) OVER (PARTITION BY col_149 ORDER BY col_170) AS col_87
FROM db_2.table_37
where col_171 <> 0 ) AS LAGGED
GROUP BY col_149
;

drop table if exists db_2.table_6;
create table db_2.table_6 AS
SELECT
col_149,
AVG(DATEDIFF(to_date(col_170),to_date(col_87))) as col_476
FROM
(SELECT 
col_149, 
col_170, 
LAG(col_170,1) OVER (PARTITION BY col_149 ORDER BY col_170) AS col_87
FROM db_2.table_37
where col_511 <> 0 ) AS LAGGED
GROUP BY col_149
;

drop table if exists db_2.table_2;
create table db_2.table_2 AS
SELECT
col_149,
AVG(DATEDIFF(to_date(col_170),to_date(col_87))) as col_476
FROM
(SELECT 
col_149, 
col_170, 
LAG(col_170,1) OVER (PARTITION BY col_149 ORDER BY col_170) AS col_87
FROM db_2.table_37
where col_522 <> 0 ) AS LAGGED
GROUP BY col_149
;

drop table if exists db_2.table_11;
create table db_2.table_11 AS
select 
usr.col_149,
coalesce(col_476,0) as col_316,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_170)))),0) as col_367,
coalesce((col_367 - col_316),0) as col_269,
COALESCE((col_367/col_316),0) as col_190
from 
db_2.table_1 USR left join
db_2.table_37 A on usr.col_149 = a.col_149 left join
db_2.table_25 B on A.col_149 = B.col_149
group by 1,2
;


-- #####3
drop table if exists db_2.table_26;
create table db_2.table_26 AS
select 
usr.col_149,
coalesce(col_476,0) as col_101,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_170)))),0) as col_26,
coalesce((col_26 - col_101),0) as col_98,
COALESCE((col_26/col_101),0) as col_26_avg_index
from 
db_2.table_1 USR left join
db_2.table_37 A on usr.col_149 = a.col_149 left join
db_2.table_34 B on A.col_149 = B.col_149
group by 1,2
;

drop table if exists db_2.table_8;
create table db_2.table_8 AS
select 
usr.col_149,
coalesce(col_476,0) as col_281,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_170)))),0) as col_352,
coalesce((col_352 - col_281),0) as col_133,
COALESCE((col_352/col_281),0) as col_352_avg_index
from 
db_2.table_1 USR left join
db_2.table_37 A on usr.col_149 = a.col_149 left join
db_2.table_38 B on A.col_149 = B.col_149
group by 1,2
;

drop table if exists db_2.table_24;
create table db_2.table_24 AS
select 
usr.col_149,
coalesce(col_476,0) as col_140,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_170)))),0) as col_436,
coalesce((col_436 - col_140),0) as col_475,
COALESCE((col_436/col_140),0) as col_436_avg_index
from 
db_2.table_1 USR left join
db_2.table_37 A on usr.col_149 = a.col_149 left join
db_2.table_13 B on A.col_149 = B.col_149
group by 1,2
;

drop table if exists db_2.table_5;
create table db_2.table_5 AS
select 
usr.col_149,
coalesce(col_476,0) as col_420,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_170)))),0) as col_489,
coalesce((col_489 - col_420),0) as col_385,
COALESCE((col_489/col_420),0) as col_94
from 
db_2.table_1 USR left join
db_2.table_37 A on usr.col_149 = a.col_149 left join
db_2.table_6 B on A.col_149 = B.col_149
group by 1,2
;

drop table if exists db_2.table_16;
create table db_2.table_16 AS
select 
usr.col_149,
coalesce(col_476,0) as col_249,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_170)))),0) as col_292,
coalesce((col_292 - col_249),0) as col_286,
COALESCE((col_292/col_249),0) as col_292_avg_index
from 
db_2.table_1 USR left join
db_2.table_37 A on usr.col_149 = a.col_149 left join
db_2.table_2 B on A.col_149 = B.col_149
group by 1,2
;

drop table if exists db_2.table_22;
create table db_2.table_22 AS
SELECT 
     CK.col_591,
     CK.col_221,
	 CK.col_120,
     CK.col_321,    
     CK.col_390,  
     CK.byr_col_381,  
     CK.slr_col_381,   
     CK.col_334 , 
     CK.col_449, 
	 CAT.col_205,
	 CAT.col_320,
	 CAT.col_146,
	 CAT.col_67,
	 CAT.col_150,
	 CAT.col_526,
	 CAT.col_113,
	 CAT.col_374,
	 CAT.col_606,
	 CAT.col_124,
	 CAT.col_219,
     SUM(col_445) AS col_545,  
     SUM(CAST((col_445 * col_78 ) AS DECIMAL(18,2))) AS GMV_B_LiC,   
     SUM(CAST((col_445 * col_78 * col_304   ) AS DECIMAL(18,2))) AS GMV_B_USD,   
	 SUM(CAST((col_445 * col_78 ) as decimal(24,6)) * LPR.col_159) AS col_173
     FROM db_1.table_10 AS CK JOIN 
   (SELECT 
     col_116 , 
     col_205,  
	 col_320,
	 col_67,
	 col_146,
	 col_526,
	 col_150,
	 col_374,
	 col_113,
	 col_606,
	 col_124,
	 col_219,
     col_275
    FROM table_3
    WHERE col_116 NOT IN (5, 7, 41,23,-999)) AS CAT  
    ON CAT.col_205 = ck.col_205 AND CAT.col_275 = ck.lstg_col_275      
	INNER JOIN db_1.table_21 lpr ON ck.col_334 = lpr.col_531
    WHERE  col_321 BETWEEN '${candidatedate}' - interval '730' day AND  '${candidatedate}' 
    AND LSTG_END_DT >= '${candidatedate}' - interval '910' day
    AND ADJ_TYPE_ID NOT IN  (3,27) 
    AND ck.INCLD_CK_YN_ID = 1
    GROUP  BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
;


-- Average days between purchases -- 
drop table if exists db_2.table_15;
create table db_2.table_15 AS
SELECT
col_120,
AVG(DATEDIFF(to_date(col_321),to_date(col_87))) as col_476
FROM
(SELECT 
col_120, 
col_321, 
LAG(col_321,1) OVER (PARTITION BY col_120 ORDER BY col_321) AS col_87
FROM db_2.table_22) AS LAGGED
GROUP BY col_120
;

drop table if exists db_2.table_12;
create table db_2.table_12 AS
select 
usr.col_149,
coalesce(col_476,0) as col_376,
coalesce((DATEDIFF(to_date('${candidatedate}'),to_date(max(A.col_321)))),0) as col_274,
coalesce((col_274 - col_376),0) as col_604,
COALESCE((col_274/col_376),0) as col_274_avg_index
from 
db_2.table_1 USR left join
db_2.table_22 A on usr.col_149 = a.col_120 left join
db_2.table_15 B on A.col_120 = B.col_120
group by 1,2
;

select * from db_2.table_22;

/*GMB and BI tranches */
drop table if exists db_2.table_17;
create table db_2.table_17 AS
select
	USR.col_149
	,'${candidatedate}' as col_267
	-- GMB
	,COALESCE(avg(col_173),0) as col_112
	,COALESCE(max(col_173),0) as col_142
	,COALESCE(min(col_173),0) as col_418
	,sum(case when col_321 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_173 else 0 end) as col_276
	,sum(case when col_321 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_173 else 0 end) as col_223
	,sum(case when col_321 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_173 else 0 end) as col_77
	,sum(case when col_321 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_173 else 0 end) as col_364
	,sum(case when col_321 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_173 else 0 end) as col_12
	,sum(case when col_321 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_173 else 0 end) as col_7
	,sum(case when col_321 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_173 else 0 end) as col_479
	,sum(case when col_321 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_173 else 0 end) as col_161
	,sum(case when col_321 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_173 else 0 end) as col_389
	,coalesce((col_276/col_112),0) as col_444
	,coalesce((col_223/col_112),0) as col_561
	,coalesce((col_77/col_112),0) as col_298
	,coalesce((col_364/col_112),0) as col_365
	,coalesce((col_12/col_112),0) as col_509
	,coalesce((col_7/col_112),0) as col_188
	,coalesce((col_276/col_142),0) as t_1w_col_142_index
	,coalesce((col_223/col_142),0) as col_1
	,coalesce((col_77/col_142),0) as col_110
	,coalesce((col_364/col_142),0) as t_4w_col_142_index
	,coalesce((col_12/col_142),0) as t_1m_2m_col_142_index
	,coalesce((col_7/col_142),0) as t_2m_3m_col_142_index
	,coalesce((col_276/col_418),0) as col_70
	,coalesce((col_223/col_418),0) as col_55
	,coalesce((col_77/col_418),0) as col_117
	,coalesce((col_364/col_418),0) as col_349
	,coalesce((col_12/col_418),0) as col_358
	,coalesce((col_7/col_418),0) as col_163
	-- SI
	,COALESCE(avg(col_545),0) as col_512
	,COALESCE(max(col_545),0) as col_408
	,COALESCE(min(col_545),0) as col_413
	,sum(case when col_321 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_545 else 0 end) as col_6
	,sum(case when col_321 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_545 else 0 end) as col_51
	,sum(case when col_321 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_545 else 0 end) as col_535
	,sum(case when col_321 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_545 else 0 end) as col_599
	,sum(case when col_321 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_545 else 0 end) as col_437
	,sum(case when col_321 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_545 else 0 end) as col_39
	,sum(case when col_321 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_545 else 0 end) as col_396
	,sum(case when col_321 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_545 else 0 end) as col_379
	,sum(case when col_321 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_545 else 0 end) as col_186
	,coalesce((col_6/col_512),0) as col_603
	,coalesce((col_51/col_512),0) as col_134
	,coalesce((col_535/col_512),0) as col_353
	,coalesce((col_599/col_512),0) as col_518
	,coalesce((col_437/col_512),0) as col_538
	,coalesce((col_39/col_512),0) as col_310
	,coalesce((col_6/col_408),0) as col_305
	,coalesce((col_51/col_408),0) as col_153
	,coalesce((col_535/col_408),0) as col_346
	,coalesce((col_599/col_408),0) as col_341
	,coalesce((col_437/col_408),0) as t_1m_2m_col_408_index
	,coalesce((col_39/col_408),0) as t_2m_3m_col_408_index
	,coalesce((col_6/col_413),0) as t_1w_col_413_index
	,coalesce((col_51/col_413),0) as col_21
	,coalesce((col_535/col_413),0) as t_3w_4w_col_413_index
	,coalesce((col_599/col_413),0) as col_243
	,coalesce((col_437/col_413),0) as col_278
	,coalesce((col_39/col_413),0) as t_2m_3m_col_413_index
from
	db_2.table_1 USR
left join
	db_2.table_22 SD
	on USR.col_149 = SD.col_120
	and SD.col_321 >= '${candidatedate}' - interval '910' day
	and sd.byr_col_381 in (-999,-1,-0,1,225,679,1000)
group by 1,2
;



-- Tenure --
drop table if exists db_2.table_29;
create table db_2.table_29 AS 
SELECT
A.col_149,
'${candidatedate}' as col_267,
coalesce(datediff(to_date('${candidatedate}'), to_date(b.col_195)),0) AS col_448
FROM db_2.table_1 A LEFT JOIN
db_1.table_40 B ON A.col_149 = B.col_149;

-- email open and click stats --
drop table if exists db_2.table_7;
create table db_2.table_7 as 
select
a.col_149
,'${candidatedate}' as col_267
,COALESCE(avg(col_342),0) as col_11
,COALESCE(max(col_342),0) as col_84
,COALESCE(min(col_342),0) as col_185
,sum(case when col_429 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_342 else 0 end) as col_340
,sum(case when col_429 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_342 else 0 end) as col_168
,sum(case when col_429 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_342 else 0 end) as t_3w_4w_col_342
,sum(case when col_429 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_342 else 0 end) as t_4w_col_342
,sum(case when col_429 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_342 else 0 end) as t_1m_2m_col_342
,sum(case when col_429 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_342 else 0 end) as t_2m_3m_col_342
,sum(case when col_429 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_342 else 0 end) as col_152
,sum(case when col_429 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_342 else 0 end) as t_6m_1y_col_342
,sum(case when col_429 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_342 else 0 end) as col_282
,coalesce((col_340/col_11),0) as col_570
,coalesce((col_168/col_11),0) as col_91
,coalesce((t_3w_4w_col_342/col_11),0) as col_244
,coalesce((t_4w_col_342/col_11),0) as col_495
,coalesce((t_1m_2m_col_342/col_11),0) as col_4
,coalesce((t_2m_3m_col_342/col_11),0) as col_329
,coalesce((col_340/col_84),0) as col_592
,coalesce((col_168/col_84),0) as col_22
,coalesce((t_3w_4w_col_342/col_84),0) as col_32
,coalesce((t_4w_col_342/col_84),0) as col_456
,coalesce((t_1m_2m_col_342/col_84),0) as col_309
,coalesce((t_2m_3m_col_342/col_84),0) as col_36
,coalesce((col_340/col_185),0) as col_17
,coalesce((col_168/col_185),0) as col_19
,coalesce((t_3w_4w_col_342/col_185),0) as col_440
,coalesce((t_4w_col_342/col_185),0) as col_89
,coalesce((t_1m_2m_col_342/col_185),0) as col_569
,coalesce((t_2m_3m_col_342/col_185),0) as col_72

,COALESCE(avg(col_247),0) as col_368
,COALESCE(max(col_247),0) as col_574
,COALESCE(min(col_247),0) as col_547
,sum(case when col_429 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_247 else 0 end) as col_69
,sum(case when col_429 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_247 else 0 end) as col_397
,sum(case when col_429 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_247 else 0 end) as col_15
,sum(case when col_429 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_247 else 0 end) as col_584
,sum(case when col_429 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_247 else 0 end) as col_202
,sum(case when col_429 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_247 else 0 end) as col_239
,sum(case when col_429 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_247 else 0 end) as col_373
,sum(case when col_429 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_247 else 0 end) as col_224
,sum(case when col_429 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_247 else 0 end) as col_254
,coalesce((col_69/col_368),0) as col_177
,coalesce((col_397/col_368),0) as col_232
,coalesce((col_15/col_368),0) as col_301
,coalesce((col_584/col_368),0) as col_102
,coalesce((col_202/col_368),0) as col_83
,coalesce((col_239/col_368),0) as col_210
,coalesce((col_69/col_574),0) as col_554
,coalesce((col_397/col_574),0) as col_435
,coalesce((col_15/col_574),0) as col_111
,coalesce((col_584/col_574),0) as col_231
,coalesce((col_202/col_574),0) as col_339
,coalesce((col_239/col_574),0) as col_90
,coalesce((col_69/col_547),0) as col_399
,coalesce((col_397/col_547),0) as col_211
,coalesce((col_15/col_547),0) as col_10
,coalesce((col_584/col_547),0) as col_144
,coalesce((col_202/col_547),0) as col_139
,coalesce((col_239/col_547),0) as col_500
from db_2.table_1 A LEFT JOIN
db_1.table_32 B ON A.col_149 = B.col_149
and B.col_429 >= '${candidatedate}' - interval '910' day
group by 1,2;

-- BBE scores --
drop table if exists db_2.table_41;
create table db_2.table_41 as 
	select
	col_120, 
	col_421,
	-- if the seller is not evaluated in this program it will be set to -1.
    -- 1-eTRS; 2-Above Standard; 3-Standard; 4-Below Standard
	COALESCE((case when col_378=1 or col_138=1 or col_291=1 or col_129 = 1 then 1 else 0 end),0) as TRX_SNAD,
	COALESCE((case when col_504=1 or col_155=1 or col_504=1 then 1 else 0 end),0) as  TRX_INR,
	COALESCE((case when col_357=1 then 1 else 0 end),0) as TRX_STOCKOUT,
	COALESCE((case when col_123=1 then 1 else 0 end),0) TRX_NN_FEEDBACK,
	COALESCE((case when col_378=1 or col_138=1 or col_291=1 or col_129 = 1 or col_504=1 or col_155=1 or col_504=1 or col_357=1 or col_123=1 then 1 else 0 end),0) col_206
from
	db_2.table_1 USR
left join
	db_3.table_39 SD
	on USR.col_149 = SD.col_120
	and SD.col_421 >= '${candidatedate}' - interval '910' day
	and SD.RPRTD_WACKO_YN_IND = 'N' 
;

drop table if exists db_2.table_27;
create table db_2.table_27 as 
select
 col_120 as col_149
,'${candidatedate}' as col_267
,COALESCE(avg(col_206),0) as col_343
,COALESCE(max(col_206),0) as col_607
,COALESCE(min(col_206),0) as col_37
,sum(case when col_421 between '${candidatedate}' - interval '7' day and '${candidatedate}' - interval '1' day then col_206 else 0 end) as col_130
,sum(case when col_421 between '${candidatedate}' - interval '14' day and '${candidatedate}' - interval '8' day then col_206 else 0 end) as col_248
,sum(case when col_421 between '${candidatedate}' - interval '30' day and '${candidatedate}' - interval '15' day then col_206 else 0 end) as col_519
,sum(case when col_421 between '${candidatedate}' - interval '28' day and '${candidatedate}' - interval '1' day then col_206 else 0 end) as col_377
,sum(case when col_421 between '${candidatedate}' - interval '60' day and '${candidatedate}' - interval '31' day then col_206 else 0 end) as col_583
,sum(case when col_421 between '${candidatedate}' - interval '90' day and '${candidatedate}' - interval '61' day then col_206 else 0 end) as col_217
,sum(case when col_421 between '${candidatedate}' - interval '180' day and '${candidatedate}' - interval '91' day then col_206 else 0 end) as col_128
,sum(case when col_421 between '${candidatedate}' - interval '365' day and '${candidatedate}' - interval '181' day then col_206 else 0 end) as col_533
,sum(case when col_421 between '${candidatedate}' - interval '730' day and '${candidatedate}' - interval '366' day then col_206 else 0 end) as col_313
,coalesce((col_130/col_343),0) as col_492
,coalesce((col_248/col_343),0) as col_536
,coalesce((col_519/col_343),0) as col_230
,coalesce((col_377/col_343),0) as col_74
,coalesce((col_583/col_343),0) as col_462
,coalesce((col_217/col_343),0) as col_613
,coalesce((col_130/col_607),0) as col_317
,coalesce((col_248/col_607),0) as col_103
,coalesce((col_519/col_607),0) as col_501
,coalesce((col_377/col_607),0) as col_459
,coalesce((col_583/col_607),0) as col_40
,coalesce((col_217/col_607),0) as col_49
,coalesce((col_130/col_37),0) as col_610
,coalesce((col_248/col_37),0) as col_252
,coalesce((col_519/col_37),0) as col_175
,coalesce((col_377/col_37),0) as col_42
,coalesce((col_583/col_37),0) as col_453
,coalesce((col_217/col_37),0) as col_314
from db_2.table_41
group by 1,2
;


-- Add all variables together --
drop table if exists db_2.table_31;
create table db_2.table_31 AS
SELECT
AA.col_149 as col_149,
A.col_267 as col_267,
COALESCE(A.col_60,0) AS col_60,
COALESCE(A.col_47,0) AS col_47,
COALESCE(A.col_95,0) AS col_95,
COALESCE(A.col_126,0) AS col_126,
COALESCE(A.t_1w_2w_col_197,0) AS t_1w_2w_col_197,
COALESCE(A.t_3w_4w_col_197,0) AS t_3w_4w_col_197,
COALESCE(A.t_4w_col_197,0) AS t_4w_col_197,
COALESCE(A.t_1m_2m_col_197,0) AS t_1m_2m_col_197,
COALESCE(A.t_2m_3m_col_197,0) AS t_2m_3m_col_197,
COALESCE(A.col_125,0) AS col_125,
COALESCE(A.t_6m_1y_col_197,0) AS t_6m_1y_col_197,
COALESCE(A.col_136,0) AS col_136,
COALESCE(A.col_608,0) AS col_608,
COALESCE(A.col_460,0) AS col_460,
COALESCE(A.col_114,0) AS col_114,
COALESCE(A.col_366,0) AS col_366,
COALESCE(A.col_348,0) AS col_348,
COALESCE(A.col_107,0) AS col_107,
COALESCE(A.col_5,0) AS col_5,
COALESCE(A.t_1w_2w_col_408d_index,0) AS t_1w_2w_col_408d_index,
COALESCE(A.col_360,0) AS col_360,
COALESCE(A.col_236,0) AS col_236,
COALESCE(A.col_135,0) AS col_135,
COALESCE(A.col_165,0) AS col_165,
COALESCE(A.t_1w_col_413d_index,0) AS t_1w_col_413d_index,
COALESCE(A.t_1w_2w_col_413d_index,0) AS t_1w_2w_col_413d_index,
COALESCE(A.col_398,0) AS col_398,
COALESCE(A.col_306,0) AS col_306,
COALESCE(A.col_79,0) AS col_79,
COALESCE(A.t_2m_3m_col_413d_index,0) AS t_2m_3m_col_413d_index,
COALESCE(A.col_53,0) AS col_53,
COALESCE(A.col_240,0) AS col_240,
COALESCE(A.min_col_362,0) AS min_col_362,
COALESCE(A.col_344,0) AS col_344,
COALESCE(A.t_1w_2w_col_362,0) AS t_1w_2w_col_362,
COALESCE(A.t_3w_4w_col_362,0) AS t_3w_4w_col_362,
COALESCE(A.col_283,0) AS col_283,
COALESCE(A.col_241,0) AS col_241,
COALESCE(A.col_52,0) AS col_52,
COALESCE(A.t_3m_6m_col_362,0) AS t_3m_6m_col_362,
COALESCE(A.col_82,0) AS col_82,
COALESCE(A.col_8,0) AS col_8,
COALESCE(A.col_473,0) AS col_473,
COALESCE(A.col_525,0) AS col_525,
COALESCE(A.col_588,0) AS col_588,
COALESCE(A.col_216,0) AS col_216,
COALESCE(A.col_502,0) AS col_502,
COALESCE(A.col_73,0) AS col_73,
COALESCE(A.col_402,0) AS col_402,
COALESCE(A.col_229,0) AS col_229,
COALESCE(A.col_263,0) AS col_263,
COALESCE(A.col_207,0) AS col_207,
COALESCE(A.col_529,0) AS col_529,
COALESCE(A.col_237,0) AS col_237,
COALESCE(A.col_590,0) AS col_590,
COALESCE(A.col_507,0) AS col_507,
COALESCE(A.col_264,0) AS col_264,
COALESCE(A.col_372,0) AS col_372,
COALESCE(A.col_296,0) AS col_296,
COALESCE(A.col_38,0) AS col_38,
COALESCE(A.col_521,0) AS col_521,
COALESCE(A.col_562,0) AS col_562,
COALESCE(A.col_330,0) AS col_330,
COALESCE(A.col_383,0) AS col_383,
COALESCE(A.col_288,0) AS col_288,
COALESCE(A.col_598,0) AS col_598,
COALESCE(A.col_178,0) AS col_178,
COALESCE(A.col_59,0) AS col_59,
COALESCE(A.col_93,0) AS col_93,
COALESCE(A.col_20,0) AS col_20,
COALESCE(A.col_485,0) AS col_485,
COALESCE(A.col_387,0) AS col_387,
COALESCE(A.col_597,0) AS col_597,
COALESCE(A.col_106,0) AS col_106,
COALESCE(A.col_108,0) AS col_108,
COALESCE(A.col_426,0) AS col_426,
COALESCE(A.col_88,0) AS col_88,
COALESCE(A.col_97,0) AS col_97,
COALESCE(A.col_404,0) AS col_404,
COALESCE(A.col_199,0) AS col_199,
COALESCE(A.col_347,0) AS col_347,
COALESCE(A.col_401,0) AS col_401,
COALESCE(A.col_515,0) AS col_515,
COALESCE(A.col_434,0) AS col_434,
COALESCE(A.col_466,0) AS col_466,
COALESCE(A.col_395,0) AS col_395,
COALESCE(A.col_54,0) AS col_54,
COALESCE(A.col_392,0) AS col_392,
COALESCE(A.col_225,0) AS col_225,
COALESCE(A.col_537,0) AS col_537,
COALESCE(A.avg_col_158,0) AS avg_col_158,
COALESCE(A.max_col_158,0) AS max_col_158,
COALESCE(A.min_col_158,0) AS min_col_158,
COALESCE(A.t_1w_col_158,0) AS t_1w_col_158,
COALESCE(A.t_1w_2w_col_158,0) AS t_1w_2w_col_158,
COALESCE(A.t_3w_4w_col_158,0) AS t_3w_4w_col_158,
COALESCE(A.col_2,0) AS col_2,
COALESCE(A.col_50,0) AS col_50,
COALESCE(A.col_121,0) AS col_121,
COALESCE(A.t_3m_6m_col_158,0) AS t_3m_6m_col_158,
COALESCE(A.t_6m_1y_col_158,0) AS t_6m_1y_col_158,
COALESCE(A.t_1y_2y_col_158,0) AS t_1y_2y_col_158,
COALESCE(A.col_201,0) AS col_201,
COALESCE(A.col_441,0) AS col_441,
COALESCE(A.col_430,0) AS col_430,
COALESCE(A.col_541,0) AS col_541,
COALESCE(A.col_265,0) AS col_265,
COALESCE(A.col_220,0) AS col_220,
COALESCE(A.col_222,0) AS col_222,
COALESCE(A.col_271,0) AS col_271,
COALESCE(A.col_614,0) AS col_614,
COALESCE(A.col_66,0) AS col_66,
COALESCE(A.col_469,0) AS col_469,
COALESCE(A.col_516,0) AS col_516,
COALESCE(A.col_24,0) AS col_24,
COALESCE(A.col_477,0) AS col_477,
COALESCE(A.col_325,0) AS col_325,
COALESCE(A.col_137,0) AS col_137,
COALESCE(A.col_99,0) AS col_99,
COALESCE(A.col_261,0) AS col_261,
COALESCE(A.col_481,0) AS col_481,
COALESCE(A.col_498,0) AS col_498,
COALESCE(A.col_143,0) AS col_143,
COALESCE(A.col_213,0) AS col_213,
COALESCE(A.col_122,0) AS col_122,
COALESCE(A.col_31,0) AS col_31,
COALESCE(A.col_327,0) AS col_327,
COALESCE(A.col_268,0) AS col_268,
COALESCE(A.col_552,0) AS col_552,
COALESCE(A.col_400,0) AS col_400,
COALESCE(A.col_578,0) AS col_578,
COALESCE(A.col_382,0) AS col_382,
COALESCE(A.col_35,0) AS col_35,
COALESCE(A.col_596,0) AS col_596,
COALESCE(A.col_127,0) AS col_127,
COALESCE(A.col_61,0) AS col_61,
COALESCE(A.col_594,0) AS col_594,
COALESCE(A.col_193,0) AS col_193,
COALESCE(A.col_335,0) AS col_335,
COALESCE(A.col_463,0) AS col_463,
COALESCE(A.col_544,0) AS col_544,
COALESCE(A.col_160,0) AS col_160,
COALESCE(A.col_494,0) AS col_494,
COALESCE(A.col_573,0) AS col_573,
COALESCE(A.col_527,0) AS col_527,
COALESCE(A.col_218,0) AS col_218,
COALESCE(A.col_43,0) AS col_43,
COALESCE(A.col_388,0) AS col_388,
COALESCE(A.col_62,0) AS col_62,
COALESCE(A.col_258,0) AS col_258,
COALESCE(A.col_191,0) AS col_191,
COALESCE(A.col_408n_cnt,0) AS col_408n_cnt,
COALESCE(A.col_234,0) AS col_234,
COALESCE(A.col_483,0) AS col_483,
COALESCE(A.col_508,0) AS col_508,
COALESCE(A.col_23,0) AS col_23,
COALESCE(A.col_272,0) AS col_272,
COALESCE(A.col_257,0) AS col_257,
COALESCE(A.col_204,0) AS col_204,
COALESCE(A.col_505,0) AS col_505,
COALESCE(A.col_16,0) AS col_16,
COALESCE(A.col_447,0) AS col_447,
COALESCE(A.col_391,0) AS col_391,
COALESCE(A.col_18,0) AS col_18,
COALESCE(A.col_577,0) AS col_577,
COALESCE(A.col_520,0) AS col_520,
COALESCE(A.col_75,0) AS col_75,
COALESCE(A.col_58,0) AS col_58,
COALESCE(A.t_1w_col_408n_index,0) AS t_1w_col_408n_index,
COALESCE(A.t_1w_2w_col_408n_index,0) AS t_1w_2w_col_408n_index,
COALESCE(A.t_3w_4w_col_408n_index,0) AS t_3w_4w_col_408n_index,
COALESCE(A.t_4w_col_408n_index,0) AS t_4w_col_408n_index,
COALESCE(A.t_1m_2m_col_408n_index,0) AS t_1m_2m_col_408n_index,
COALESCE(A.t_2m_3m_col_408n_index,0) AS t_2m_3m_col_408n_index,
COALESCE(A.col_76,0) AS col_76,
COALESCE(A.col_27,0) AS col_27,
COALESCE(A.col_405,0) AS col_405,
COALESCE(A.t_4w_col_413n_index,0) AS t_4w_col_413n_index,
COALESCE(A.t_1m_2m_col_413n_index,0) AS t_1m_2m_col_413n_index,
COALESCE(A.col_297,0) AS col_297,
COALESCE(B.col_290,0) AS col_290,
COALESCE(B.col_183,0) AS col_183,
COALESCE(B.col_147,0) AS col_147,
COALESCE(B.col_156,0) AS col_156,
COALESCE(B.col_386,0) AS col_386,
COALESCE(B.col_530,0) AS col_530,
COALESCE(B.col_14,0) AS col_14,
COALESCE(B.col_576,0) AS col_576,
COALESCE(B.col_194,0) AS col_194,
COALESCE(B.col_412,0) AS col_412,
COALESCE(B.col_253,0) AS col_253,
COALESCE(B.col_609,0) AS col_609,
COALESCE(B.col_595,0) AS col_595,
COALESCE(B.col_567,0) AS col_567,
COALESCE(B.col_439,0) AS col_439,
COALESCE(B.col_380,0) AS col_380,
COALESCE(B.col_517,0) AS col_517,
COALESCE(B.col_100,0) AS col_100,
COALESCE(B.col_410,0) AS col_410,
COALESCE(B.col_414,0) AS col_414,
COALESCE(B.col_417,0) AS col_417,
COALESCE(B.col_454,0) AS col_454,
COALESCE(B.col_350,0) AS col_350,
COALESCE(B.col_432,0) AS col_432,
COALESCE(B.col_354,0) AS col_354,
COALESCE(B.col_56,0) AS col_56,
COALESCE(B.col_64,0) AS col_64,
COALESCE(B.col_605,0) AS col_605,
COALESCE(B.col_176,0) AS col_176,
COALESCE(B.col_192,0) AS col_192,
COALESCE(B.col_86,0) AS col_86,
COALESCE(B.col_307,0) AS col_307,
COALESCE(B.col_438,0) AS col_438,
COALESCE(B.col_560,0) AS col_560,
COALESCE(B.col_315,0) AS col_315,
COALESCE(B.col_338,0) AS col_338,
COALESCE(B.col_571,0) AS col_571,
COALESCE(B.col_299,0) AS col_299,
COALESCE(B.col_580,0) AS col_580,
COALESCE(B.col_270,0) AS col_270,
COALESCE(B.col_260,0) AS col_260,
COALESCE(B.col_600,0) AS col_600,
COALESCE(B.col_256,0) AS col_256,
COALESCE(B.col_80,0) AS col_80,
COALESCE(B.col_251,0) AS col_251,
COALESCE(B.col_617,0) AS col_617,
COALESCE(B.col_345,0) AS col_345,
COALESCE(B.col_496,0) AS col_496,
COALESCE(B.col_105,0) AS col_105,
COALESCE(B.col_455,0) AS col_455,
COALESCE(B.col_118,0) AS col_118,
COALESCE(B.col_370,0) AS col_370,
COALESCE(B.col_28,0) AS col_28,
COALESCE(B.col_13,0) AS col_13,
COALESCE(B.col_212,0) AS col_212,
COALESCE(B.col_189,0) AS col_189,
COALESCE(B.col_198,0) AS col_198,
COALESCE(B.col_63,0) AS col_63,
COALESCE(B.col_423,0) AS col_423,
COALESCE(B.col_443,0) AS col_443,
COALESCE(B.col_9,0) AS col_9,
COALESCE(B.col_363,0) AS col_363,
COALESCE(B.col_312,0) AS col_312,
COALESCE(B.col_471,0) AS col_471,
COALESCE(B.col_300,0) AS col_300,
COALESCE(B.col_215,0) AS col_215,
COALESCE(B.col_96,0) AS col_96,
COALESCE(B.col_458,0) AS col_458,
COALESCE(B.col_277,0) AS col_277,
COALESCE(B.col_141,0) AS col_141,
COALESCE(B.col_355,0) AS col_355,
COALESCE(B.col_48,0) AS col_48,
COALESCE(B.col_394,0) AS col_394,
COALESCE(B.col_166,0) AS col_166,
COALESCE(B.col_233,0) AS col_233,
COALESCE(B.col_174,0) AS col_174,
COALESCE(B.col_490,0) AS col_490,
COALESCE(B.col_151,0) AS col_151,
COALESCE(B.col_187,0) AS col_187,
COALESCE(B.col_532,0) AS col_532,
COALESCE(B.col_308,0) AS col_308,
COALESCE(B.col_433,0) AS col_433,
COALESCE(B.col_132,0) AS col_132,
COALESCE(B.col_572,0) AS col_572,
COALESCE(B.col_311,0) AS col_311,
COALESCE(B.col_266,0) AS col_266,
COALESCE(B.col_371,0) AS col_371,
COALESCE(B.col_30,0) AS col_30,
COALESCE(B.col_556,0) AS col_556,
COALESCE(B.col_181,0) AS col_181,
COALESCE(B.avg_col_171,0) AS avg_col_171,
COALESCE(B.max_col_171,0) AS max_col_171,
COALESCE(B.min_col_171,0) AS min_col_171,
COALESCE(B.t_1w_col_171,0) AS t_1w_col_171,
COALESCE(B.col_33,0) AS col_33,
COALESCE(B.t_3w_4w_col_171,0) AS t_3w_4w_col_171,
COALESCE(B.t_4w_col_171,0) AS t_4w_col_171,
COALESCE(B.t_1m_2m_col_171,0) AS t_1m_2m_col_171,
COALESCE(B.t_2m_3m_col_171,0) AS t_2m_3m_col_171,
COALESCE(B.t_3m_6m_col_171,0) AS t_3m_6m_col_171,
COALESCE(B.t_6m_1y_col_171,0) AS t_6m_1y_col_171,
COALESCE(B.col_57,0) AS col_57,
COALESCE(B.col_431,0) AS col_431,
COALESCE(B.col_510,0) AS col_510,
COALESCE(B.col_164,0) AS col_164,
COALESCE(B.col_474,0) AS col_474,
COALESCE(B.col_409,0) AS col_409,
COALESCE(B.col_513,0) AS col_513,
COALESCE(B.col_34,0) AS col_34,
COALESCE(B.col_406,0) AS col_406,
COALESCE(B.col_3,0) AS col_3,
COALESCE(B.col_184,0) AS col_184,
COALESCE(B.col_451,0) AS col_451,
COALESCE(B.col_470,0) AS col_470,
COALESCE(B.col_284,0) AS col_284,
COALESCE(B.col_461,0) AS col_461,
COALESCE(B.col_172,0) AS col_172,
COALESCE(B.col_549,0) AS col_549,
COALESCE(B.col_581,0) AS col_581,
COALESCE(B.col_242,0) AS col_242,
COALESCE(B.col_214,0) AS col_214,
COALESCE(B.col_259,0) AS col_259,
COALESCE(B.col_351,0) AS col_351,
COALESCE(B.col_403,0) AS col_403,
COALESCE(B.col_245,0) AS col_245,
COALESCE(B.col_280,0) AS col_280,
COALESCE(B.col_109,0) AS col_109,
COALESCE(B.col_457,0) AS col_457,
COALESCE(B.col_356,0) AS col_356,
COALESCE(B.col_226,0) AS col_226,
COALESCE(B.col_29,0) AS col_29,
COALESCE(B.col_71,0) AS col_71,
COALESCE(B.col_450,0) AS col_450,
COALESCE(B.col_228,0) AS col_228,
COALESCE(B.col_491,0) AS col_491,
COALESCE(B.col_415,0) AS col_415,
COALESCE(B.col_209,0) AS col_209,
COALESCE(B.col_478,0) AS col_478,
COALESCE(B.col_262,0) AS col_262,
COALESCE(B.col_563,0) AS col_563,
COALESCE(B.col_506,0) AS col_506,
COALESCE(B.col_323,0) AS col_323,
COALESCE(B.col_167,0) AS col_167,
COALESCE(B.col_65,0) AS col_65,
COALESCE(B.col_104,0) AS col_104,
COALESCE(B.col_486,0) AS col_486,
COALESCE(B.col_44,0) AS col_44,
COALESCE(B.col_238,0) AS col_238,
COALESCE(B.col_169,0) AS col_169,
COALESCE(B.col_558,0) AS col_558,
COALESCE(B.avg_col_522,0) AS avg_col_522,
COALESCE(B.col_255,0) AS col_255,
COALESCE(B.min_col_522,0) AS min_col_522,
COALESCE(B.col_148,0) AS col_148,
COALESCE(B.t_1w_2w_col_522,0) AS t_1w_2w_col_522,
COALESCE(B.col_294,0) AS col_294,
COALESCE(B.t_4w_col_522,0) AS t_4w_col_522,
COALESCE(B.t_1m_2m_col_522,0) AS t_1m_2m_col_522,
COALESCE(B.t_2m_3m_col_522,0) AS t_2m_3m_col_522,
COALESCE(B.col_293,0) AS col_293,
COALESCE(B.t_6m_1y_col_522,0) AS t_6m_1y_col_522,
COALESCE(B.col_92,0) AS col_92,
COALESCE(B.col_465,0) AS col_465,
COALESCE(B.col_326,0) AS col_326,
COALESCE(B.col_85,0) AS col_85,
COALESCE(B.col_45,0) AS col_45,
COALESCE(B.col_68,0) AS col_68,
COALESCE(B.col_115,0) AS col_115,
COALESCE(B.col_196,0) AS col_196,
COALESCE(B.col_369,0) AS col_369,
COALESCE(B.col_145,0) AS col_145,
COALESCE(B.col_289,0) AS col_289,
COALESCE(B.col_81,0) AS col_81,
COALESCE(B.col_587,0) AS col_587,
COALESCE(B.col_331,0) AS col_331,
COALESCE(B.col_539,0) AS col_539,
COALESCE(B.col_336,0) AS col_336,
COALESCE(B.col_157,0) AS col_157,
COALESCE(B.col_337,0) AS col_337,
COALESCE(B.col_250,0) AS col_250,
COALESCE(C.col_112,0) AS col_112,
COALESCE(C.col_142,0) AS col_142,
COALESCE(C.col_418,0) AS col_418,
COALESCE(C.col_276,0) AS col_276,
COALESCE(C.col_223,0) AS col_223,
COALESCE(C.col_77,0) AS col_77,
COALESCE(C.col_364,0) AS col_364,
COALESCE(C.col_12,0) AS col_12,
COALESCE(C.col_7,0) AS col_7,
COALESCE(C.col_479,0) AS col_479,
COALESCE(C.col_161,0) AS col_161,
COALESCE(C.col_389,0) AS col_389,
COALESCE(C.col_444,0) AS col_444,
COALESCE(C.col_561,0) AS col_561,
COALESCE(C.col_298,0) AS col_298,
COALESCE(C.col_365,0) AS col_365,
COALESCE(C.col_509,0) AS col_509,
COALESCE(C.col_188,0) AS col_188,
COALESCE(C.t_1w_col_142_index,0) AS t_1w_col_142_index,
COALESCE(C.col_1,0) AS col_1,
COALESCE(C.col_110,0) AS col_110,
COALESCE(C.t_4w_col_142_index,0) AS t_4w_col_142_index,
COALESCE(C.t_1m_2m_col_142_index,0) AS t_1m_2m_col_142_index,
COALESCE(C.t_2m_3m_col_142_index,0) AS t_2m_3m_col_142_index,
COALESCE(C.col_70,0) AS col_70,
COALESCE(C.col_55,0) AS col_55,
COALESCE(C.col_117,0) AS col_117,
COALESCE(C.col_349,0) AS col_349,
COALESCE(C.col_358,0) AS col_358,
COALESCE(C.col_163,0) AS col_163,
COALESCE(C.col_512,0) AS col_512,
COALESCE(C.col_408,0) AS col_408,
COALESCE(C.col_413,0) AS col_413,
COALESCE(C.col_6,0) AS col_6,
COALESCE(C.col_51,0) AS col_51,
COALESCE(C.col_535,0) AS col_535,
COALESCE(C.col_599,0) AS col_599,
COALESCE(C.col_437,0) AS col_437,
COALESCE(C.col_39,0) AS col_39,
COALESCE(C.col_396,0) AS col_396,
COALESCE(C.col_379,0) AS col_379,
COALESCE(C.col_186,0) AS col_186,
COALESCE(C.col_603,0) AS col_603,
COALESCE(C.col_134,0) AS col_134,
COALESCE(C.col_353,0) AS col_353,
COALESCE(C.col_518,0) AS col_518,
COALESCE(C.col_538,0) AS col_538,
COALESCE(C.col_310,0) AS col_310,
COALESCE(C.col_305,0) AS col_305,
COALESCE(C.col_153,0) AS col_153,
COALESCE(C.col_346,0) AS col_346,
COALESCE(C.col_341,0) AS col_341,
COALESCE(C.t_1m_2m_col_408_index,0) AS t_1m_2m_col_408_index,
COALESCE(C.t_2m_3m_col_408_index,0) AS t_2m_3m_col_408_index,
COALESCE(C.t_1w_col_413_index,0) AS t_1w_col_413_index,
COALESCE(C.col_21,0) AS col_21,
COALESCE(C.t_3w_4w_col_413_index,0) AS t_3w_4w_col_413_index,
COALESCE(C.col_243,0) AS col_243,
COALESCE(C.col_278,0) AS col_278,
COALESCE(C.t_2m_3m_col_413_index,0) AS t_2m_3m_col_413_index,
COALESCE(E.col_376,0) AS col_376,
COALESCE(E.col_274,0) AS col_274,
COALESCE(E.col_604,0) AS col_604,
COALESCE(E.col_274_avg_index,0) AS col_274_avg_index,
COALESCE(G.col_11,0) AS col_11,
COALESCE(G.col_84,0) AS col_84,
COALESCE(G.col_185,0) AS col_185,
COALESCE(G.col_340,0) AS col_340,
COALESCE(G.col_168,0) AS col_168,
COALESCE(G.t_3w_4w_col_342,0) AS t_3w_4w_col_342,
COALESCE(G.t_4w_col_342,0) AS t_4w_col_342,
COALESCE(G.t_1m_2m_col_342,0) AS t_1m_2m_col_342,
COALESCE(G.t_2m_3m_col_342,0) AS t_2m_3m_col_342,
COALESCE(G.col_152,0) AS col_152,
COALESCE(G.t_6m_1y_col_342,0) AS t_6m_1y_col_342,
COALESCE(G.col_282,0) AS col_282,
COALESCE(G.col_570,0) AS col_570,
COALESCE(G.col_91,0) AS col_91,
COALESCE(G.col_244,0) AS col_244,
COALESCE(G.col_495,0) AS col_495,
COALESCE(G.col_4,0) AS col_4,
COALESCE(G.col_329,0) AS col_329,
COALESCE(G.col_592,0) AS col_592,
COALESCE(G.col_22,0) AS col_22,
COALESCE(G.col_32,0) AS col_32,
COALESCE(G.col_456,0) AS col_456,
COALESCE(G.col_309,0) AS col_309,
COALESCE(G.col_36,0) AS col_36,
COALESCE(G.col_17,0) AS col_17,
COALESCE(G.col_19,0) AS col_19,
COALESCE(G.col_440,0) AS col_440,
COALESCE(G.col_89,0) AS col_89,
COALESCE(G.col_569,0) AS col_569,
COALESCE(G.col_72,0) AS col_72,
COALESCE(G.col_368,0) AS col_368,
COALESCE(G.col_574,0) AS col_574,
COALESCE(G.col_547,0) AS col_547,
COALESCE(G.col_69,0) AS col_69,
COALESCE(G.col_397,0) AS col_397,
COALESCE(G.col_15,0) AS col_15,
COALESCE(G.col_584,0) AS col_584,
COALESCE(G.col_202,0) AS col_202,
COALESCE(G.col_239,0) AS col_239,
COALESCE(G.col_373,0) AS col_373,
COALESCE(G.col_224,0) AS col_224,
COALESCE(G.col_254,0) AS col_254,
COALESCE(G.col_177,0) AS col_177,
COALESCE(G.col_232,0) AS col_232,
COALESCE(G.col_301,0) AS col_301,
COALESCE(G.col_102,0) AS col_102,
COALESCE(G.col_83,0) AS col_83,
COALESCE(G.col_210,0) AS col_210,
COALESCE(G.col_554,0) AS col_554,
COALESCE(G.col_435,0) AS col_435,
COALESCE(G.col_111,0) AS col_111,
COALESCE(G.col_231,0) AS col_231,
COALESCE(G.col_339,0) AS col_339,
COALESCE(G.col_90,0) AS col_90,
COALESCE(G.col_399,0) AS col_399,
COALESCE(G.col_211,0) AS col_211,
COALESCE(G.col_10,0) AS col_10,
COALESCE(G.col_144,0) AS col_144,
COALESCE(G.col_139,0) AS col_139,
COALESCE(G.col_500,0) AS col_500,
COALESCE(I.col_343,0) AS col_343,
COALESCE(I.col_607,0) AS col_607,
COALESCE(I.col_37,0) AS col_37,
COALESCE(I.col_130,0) AS col_130,
COALESCE(I.col_248,0) AS col_248,
COALESCE(I.col_519,0) AS col_519,
COALESCE(I.col_377,0) AS col_377,
COALESCE(I.col_583,0) AS col_583,
COALESCE(I.col_217,0) AS col_217,
COALESCE(I.col_128,0) AS col_128,
COALESCE(I.col_533,0) AS col_533,
COALESCE(I.col_313,0) AS col_313,
COALESCE(I.col_492,0) AS col_492,
COALESCE(I.col_536,0) AS col_536,
COALESCE(I.col_230,0) AS col_230,
COALESCE(I.col_74,0) AS col_74,
COALESCE(I.col_462,0) AS col_462,
COALESCE(I.col_613,0) AS col_613,
COALESCE(I.col_317,0) AS col_317,
COALESCE(I.col_103,0) AS col_103,
COALESCE(I.col_501,0) AS col_501,
COALESCE(I.col_459,0) AS col_459,
COALESCE(I.col_40,0) AS col_40,
COALESCE(I.col_49,0) AS col_49,
COALESCE(I.col_610,0) AS col_610,
COALESCE(I.col_252,0) AS col_252,
COALESCE(I.col_175,0) AS col_175,
COALESCE(I.col_42,0) AS col_42,
COALESCE(I.col_453,0) AS col_453,
COALESCE(I.col_314,0) AS col_314,
coalesce((B.col_156/C.col_6),0) as t_1w_vi_bi,
coalesce((B.col_386/C.col_51),0) as t_1w_2w_vi_bi,
coalesce((B.col_530/C.col_535),0) as t_3w_4w_vi_bi,
coalesce((B.col_14/C.col_535),0) as t_4w_vi_bi,
coalesce((B.col_576/C.col_437),0) as t_1m_2m_vi_bi,
coalesce((B.col_194/C.col_39),0) as t_2m_3m_vi_bi,
coalesce((B.col_560/C.col_6),0) as t_1w_srch_bi,
coalesce((B.col_315/C.col_51),0) as t_1w_2w_srch_bi,
coalesce((B.col_338/C.col_535),0) as t_3w_4w_srch_bi,
coalesce((B.col_571/C.col_535),0) as t_4w_srch_bi,
coalesce((B.col_299/C.col_437),0) as t_1m_2m_srch_bi,
coalesce((B.col_580/C.col_39),0) as t_2m_3m_srch_bi,
coalesce((C.col_276/C.col_6),0) as t_1w_gmb_bi,
coalesce((C.col_223/C.col_51),0) as t_1w_2w_gmb_bi,
coalesce((C.col_77/C.col_535),0) as t_3w_4w_gmb_bi,
coalesce((C.col_364/C.col_535),0) as t_4w_gmb_bi,
coalesce((C.col_12/C.col_437),0) as t_1m_2m_gmb_bi,
coalesce((C.col_7/C.col_39),0) as t_2m_3m_gmb_bi,
coalesce(F.col_448,0) as col_448,
coalesce(J.col_316,0) as col_316,
coalesce(J.col_367,0) as col_367,
coalesce(J.col_269,0) as col_269,
coalesce(J.col_190,0) as col_190,
coalesce(K.col_101,0) as col_101,
coalesce(K.col_26,0) as col_26,
coalesce(K.col_98,0) as col_98,
coalesce(K.col_26_avg_index,0) as col_26_avg_index,
coalesce(L.col_281,0) as col_281,
coalesce(L.col_352,0) as col_352,
coalesce(L.col_133,0) as col_133,
coalesce(L.col_352_avg_index,0) as col_352_avg_index,
coalesce(M.col_140,0) as col_140,
coalesce(M.col_436,0) as col_436,
coalesce(M.col_475,0) as col_475,
coalesce(M.col_436_avg_index,0) as col_436_avg_index,
coalesce(N.col_420,0) as col_420,
coalesce(N.col_489,0) as col_489,
coalesce(N.col_385,0) as col_385,
coalesce(N.col_94,0) as col_94,
coalesce(O.col_249,0) as col_249,
coalesce(O.col_292,0) as col_292,
coalesce(O.col_286,0) as col_286,
coalesce(O.col_292_avg_index,0) as col_292_avg_index
from
db_2.table_1 AA LEFT JOIN 
db_2.table_14 A ON AA.col_149 = A.col_149 LEFT JOIN 
db_2.table_23 B ON A.col_149 = B.col_149 LEFT JOIN 
db_2.table_17 C ON B.col_149 = C.col_149 LEFT JOIN
db_2.table_12 E ON C.col_149 = E.col_149 LEFT JOIN
db_2.table_29 F ON E.col_149 = F.col_149 LEFT JOIN
db_2.table_7 G ON F.col_149 = G.col_149 LEFT JOIN
db_2.table_27 I ON G.col_149 = I.col_149 LEFT JOIN
db_2.table_11 J ON I.col_149 = J.col_149 LEFT JOIN
db_2.table_26 K ON J.col_149 = K.col_149 LEFT JOIN
db_2.table_8 L ON K.col_149 = L.col_149 LEFT JOIN
db_2.table_24 M ON L.col_149 = M.col_149 LEFT JOIN
db_2.table_5 N ON M.col_149 = N.col_149 LEFT JOIN
db_2.table_16 O ON N.col_149 = O.col_149 
;

drop table if exists db_2.table_33;
CREATE table db_2.table_33 AS
SELECT 
	 CK.col_120,
     CK.col_321,    
     CK.byr_col_381,  
     CK.slr_col_381,   
     SUM(col_445) AS col_545,  
     SUM(CAST((col_445 * col_78 ) AS DECIMAL(18,2))) AS GMV_B_LiC,   
     SUM(CAST((col_445 * col_78 * col_304   ) AS DECIMAL(18,2))) AS GMV_B_USD,   
	 SUM(CAST((col_445 * col_78 ) as decimal(24,6)) * LPR.col_159) AS col_173
     FROM db_1.table_10 AS CK JOIN 
   (SELECT 
     col_116 , 
     col_205,  
	 col_320,
	 col_67,
	 col_146,
	 col_526,
	 col_150,
	 col_374,
	 col_113,
	 col_606,
	 col_124,
	 col_219,
     col_275
    FROM table_3
    WHERE col_116 NOT IN (5, 7, 41,23,-999)) AS CAT  
    ON CAT.col_205 = ck.col_205 AND CAT.col_275 = ck.lstg_col_275      
	INNER JOIN db_1.table_21 lpr ON ck.col_334 = lpr.col_531
    WHERE  col_321 BETWEEN '${candidatedate}' AND  '${candidatedate}' + interval '365' day
    AND LSTG_END_DT >= '${candidatedate}' - interval '365' day
    AND ADJ_TYPE_ID NOT IN  (3,27) 
    AND ck.INCLD_CK_YN_ID = 1
    GROUP  BY 1,2,3,4
;



drop table if exists db_2.table_9;
create table db_2.table_9 as
select  
distinct
col_120,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '14' day then 1 else 0 end) as col_41,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '30' day then 1 else 0 end) as col_322,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '28' day then 1 else 0 end) as col_559,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '60' day then 1 else 0 end) as col_131,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '90' day then 1 else 0 end) as col_25,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '180' day then 1 else 0 end) as col_488,
sum(case when col_321 between '${candidatedate}' + interval '1' day and '${candidatedate}' + interval '365' day then 1 else 0 end) as col_273
from db_2.table_33
group by 1
;

drop table if exists db_2.table_20;
create table db_2.table_20 as
select
distinct 
col_120,
(case when col_41 >= 1 then 1 else 0 end) as col_41,
(case when col_322 >= 1 then 1 else 0 end) as col_322,
(case when col_559 >= 1 then 1 else 0 end) as col_559,
(case when col_131 >= 1 then 1 else 0 end) as col_131,
(case when col_25 >= 1 then 1 else 0 end) as col_25,
(case when col_488 >= 1 then 1 else 0 end) as col_488,
(case when col_273 >= 1 then 1 else 0 end) as col_273
from db_2.table_9
;


create table db_2.table_35 as
select
distinct
a.*,
COALESCE(b.col_41,0) as col_41,
COALESCE(b.col_322,0) as col_322,
COALESCE(b.col_322,0) as col_559,
COALESCE(b.col_131,0) as col_131,
COALESCE(b.col_25,0) as col_25,
COALESCE(b.col_488,0) as col_488,
COALESCE(b.col_273,0) as col_273
from db_2.table_31 a
LEFT JOIN db_2.table_20 b 
on a.col_149 = b.col_120 ;

select * from db_2.table_35 where col_559>0;