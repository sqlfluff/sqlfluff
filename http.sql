#standardSQL
# 07_04d: % fast FID per PSI by geo
WITH geos AS (
  SELECT *, 'af' AS geo_code, 'Afghanistan' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_af.201907` UNION ALL
  SELECT *, 'ax' AS geo_code, 'Åland Islands' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_ax.201907` UNION ALL
  SELECT *, 'al' AS geo_code, 'Albania' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_al.201907` UNION ALL
  SELECT *, 'dz' AS geo_code, 'Algeria' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_dz.201907` UNION ALL
  SELECT *, 'as' AS geo_code, 'American Samoa' AS geo, 'Oceania' AS region, 'Polynesia' AS subregion FROM `chrome-ux-report.country_as.201907` UNION ALL
  SELECT *, 'ad' AS geo_code, 'Andorra' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_ad.201907` UNION ALL
  SELECT *, 'ao' AS geo_code, 'Angola' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_ao.201907` UNION ALL
  SELECT *, 'ai' AS geo_code, 'Anguilla' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_ai.201907` UNION ALL
  SELECT *, 'ag' AS geo_code, 'Antigua and Barbuda' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_ag.201907` UNION ALL
  SELECT *, 'ar' AS geo_code, 'Argentina' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_ar.201907` UNION ALL
  SELECT *, 'am' AS geo_code, 'Armenia' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_am.201907` UNION ALL
  SELECT *, 'aw' AS geo_code, 'Aruba' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_aw.201907` UNION ALL
  SELECT *, 'au' AS geo_code, 'Australia' AS geo, 'Oceania' AS region, 'Australia and New Zealand' AS subregion FROM `chrome-ux-report.country_au.201907` UNION ALL
  SELECT *, 'at' AS geo_code, 'Austria' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_at.201907` UNION ALL
  SELECT *, 'az' AS geo_code, 'Azerbaijan' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_az.201907` UNION ALL
  SELECT *, 'bs' AS geo_code, 'Bahamas' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_bs.201907` UNION ALL
  SELECT *, 'bh' AS geo_code, 'Bahrain' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_bh.201907` UNION ALL
  SELECT *, 'bd' AS geo_code, 'Bangladesh' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_bd.201907` UNION ALL
  SELECT *, 'bb' AS geo_code, 'Barbados' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_bb.201907` UNION ALL
  SELECT *, 'by' AS geo_code, 'Belarus' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_by.201907` UNION ALL
  SELECT *, 'be' AS geo_code, 'Belgium' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_be.201907` UNION ALL
  SELECT *, 'bz' AS geo_code, 'Belize' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_bz.201907` UNION ALL
  SELECT *, 'bj' AS geo_code, 'Benin' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_bj.201907` UNION ALL
  SELECT *, 'bm' AS geo_code, 'Bermuda' AS geo, 'Americas' AS region, 'Northern America' AS subregion FROM `chrome-ux-report.country_bm.201907` UNION ALL
  SELECT *, 'bt' AS geo_code, 'Bhutan' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_bt.201907` UNION ALL
  SELECT *, 'bo' AS geo_code, 'Bolivia (Plurinational State of)' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_bo.201907` UNION ALL
  SELECT *, 'bq' AS geo_code, 'Bonaire, Sint Eustatius and Saba' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_bq.201907` UNION ALL
  SELECT *, 'ba' AS geo_code, 'Bosnia and Herzegovina' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_ba.201907` UNION ALL
  SELECT *, 'bw' AS geo_code, 'Botswana' AS geo, 'Africa' AS region, 'Southern Africa' AS subregion FROM `chrome-ux-report.country_bw.201907` UNION ALL
  SELECT *, 'br' AS geo_code, 'Brazil' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_br.201907` UNION ALL
  SELECT *, 'io' AS geo_code, 'British Indian Ocean Territory' AS geo, '' AS region, 'null' AS subregion FROM `chrome-ux-report.country_io.201907` UNION ALL
  SELECT *, 'bn' AS geo_code, 'Brunei Darussalam' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_bn.201907` UNION ALL
  SELECT *, 'bg' AS geo_code, 'Kosovo' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_bg.201907` UNION ALL
  SELECT *, 'bf' AS geo_code, 'Burkina Faso' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_bf.201907` UNION ALL
  SELECT *, 'bi' AS geo_code, 'Burundi' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_bi.201907` UNION ALL
  SELECT *, 'kh' AS geo_code, 'Cambodia' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_kh.201907` UNION ALL
  SELECT *, 'cm' AS geo_code, 'Cameroon' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_cm.201907` UNION ALL
  SELECT *, 'ca' AS geo_code, 'Canada' AS geo, 'Americas' AS region, 'Northern America' AS subregion FROM `chrome-ux-report.country_ca.201907` UNION ALL
  SELECT *, 'cv' AS geo_code, 'Cabo Verde' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_cv.201907` UNION ALL
  SELECT *, 'ky' AS geo_code, 'Cayman Islands' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_ky.201907` UNION ALL
  SELECT *, 'cf' AS geo_code, 'Central African Republic' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_cf.201907` UNION ALL
  SELECT *, 'td' AS geo_code, 'Chad' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_td.201907` UNION ALL
  SELECT *, 'cl' AS geo_code, 'Chile' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_cl.201907` UNION ALL
  SELECT *, 'cn' AS geo_code, 'China' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_cn.201907` UNION ALL
  SELECT *, 'cx' AS geo_code, 'Christmas Island' AS geo, '' AS region, 'null' AS subregion FROM `chrome-ux-report.country_cx.201907` UNION ALL
  SELECT *, 'co' AS geo_code, 'Colombia' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_co.201907` UNION ALL
  SELECT *, 'km' AS geo_code, 'Comoros' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_km.201907` UNION ALL
  SELECT *, 'cg' AS geo_code, 'Congo' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_cg.201907` UNION ALL
  SELECT *, 'cd' AS geo_code, 'Congo (Democratic Republic of the)' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_cd.201907` UNION ALL
  SELECT *, 'ck' AS geo_code, 'Cook Islands' AS geo, 'Oceania' AS region, 'Polynesia' AS subregion FROM `chrome-ux-report.country_ck.201907` UNION ALL
  SELECT *, 'cr' AS geo_code, 'Costa Rica' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_cr.201907` UNION ALL
  SELECT *, 'ci' AS geo_code, 'Côte d\'Ivoire' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_ci.201907` UNION ALL
  SELECT *, 'hr' AS geo_code, 'Croatia' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_hr.201907` UNION ALL
  SELECT *, 'cu' AS geo_code, 'Cuba' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_cu.201907` UNION ALL
  SELECT *, 'cw' AS geo_code, 'Curaçao' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_cw.201907` UNION ALL
  SELECT *, 'cy' AS geo_code, 'Cyprus' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_cy.201907` UNION ALL
  SELECT *, 'cz' AS geo_code, 'Czech Republic' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_cz.201907` UNION ALL
  SELECT *, 'dk' AS geo_code, 'Denmark' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_dk.201907` UNION ALL
  SELECT *, 'dj' AS geo_code, 'Djibouti' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_dj.201907` UNION ALL
  SELECT *, 'dm' AS geo_code, 'Dominica' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_dm.201907` UNION ALL
  SELECT *, 'do' AS geo_code, 'Dominican Republic' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_do.201907` UNION ALL
  SELECT *, 'ec' AS geo_code, 'Ecuador' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_ec.201907` UNION ALL
  SELECT *, 'eg' AS geo_code, 'Egypt' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_eg.201907` UNION ALL
  SELECT *, 'sv' AS geo_code, 'El Salvador' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_sv.201907` UNION ALL
  SELECT *, 'gq' AS geo_code, 'Equatorial Guinea' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_gq.201907` UNION ALL
  SELECT *, 'er' AS geo_code, 'Eritrea' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_er.201907` UNION ALL
  SELECT *, 'ee' AS geo_code, 'Estonia' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_ee.201907` UNION ALL
  SELECT *, 'et' AS geo_code, 'Ethiopia' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_et.201907` UNION ALL
  SELECT *, 'fk' AS geo_code, 'Falkland Islands (Malvinas)' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_fk.201907` UNION ALL
  SELECT *, 'fo' AS geo_code, 'Faroe Islands' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_fo.201907` UNION ALL
  SELECT *, 'fj' AS geo_code, 'Fiji' AS geo, 'Oceania' AS region, 'Melanesia' AS subregion FROM `chrome-ux-report.country_fj.201907` UNION ALL
  SELECT *, 'fi' AS geo_code, 'Finland' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_fi.201907` UNION ALL
  SELECT *, 'fr' AS geo_code, 'France' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_fr.201907` UNION ALL
  SELECT *, 'gf' AS geo_code, 'French Guiana' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_gf.201907` UNION ALL
  SELECT *, 'pf' AS geo_code, 'French Polynesia' AS geo, 'Oceania' AS region, 'Polynesia' AS subregion FROM `chrome-ux-report.country_pf.201907` UNION ALL
  SELECT *, 'ga' AS geo_code, 'Gabon' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_ga.201907` UNION ALL
  SELECT *, 'gm' AS geo_code, 'Gambia' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_gm.201907` UNION ALL
  SELECT *, 'ge' AS geo_code, 'Georgia' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_ge.201907` UNION ALL
  SELECT *, 'de' AS geo_code, 'Germany' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_de.201907` UNION ALL
  SELECT *, 'gh' AS geo_code, 'Ghana' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_gh.201907` UNION ALL
  SELECT *, 'gi' AS geo_code, 'Gibraltar' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_gi.201907` UNION ALL
  SELECT *, 'gr' AS geo_code, 'Greece' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_gr.201907` UNION ALL
  SELECT *, 'gl' AS geo_code, 'Greenland' AS geo, 'Americas' AS region, 'Northern America' AS subregion FROM `chrome-ux-report.country_gl.201907` UNION ALL
  SELECT *, 'gd' AS geo_code, 'Grenada' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_gd.201907` UNION ALL
  SELECT *, 'gp' AS geo_code, 'Guadeloupe' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_gp.201907` UNION ALL
  SELECT *, 'gu' AS geo_code, 'Guam' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_gu.201907` UNION ALL
  SELECT *, 'gt' AS geo_code, 'Guatemala' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_gt.201907` UNION ALL
  SELECT *, 'gg' AS geo_code, 'Guernsey' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_gg.201907` UNION ALL
  SELECT *, 'gn' AS geo_code, 'Guinea' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_gn.201907` UNION ALL
  SELECT *, 'gw' AS geo_code, 'Guinea-Bissau' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_gw.201907` UNION ALL
  SELECT *, 'gy' AS geo_code, 'Guyana' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_gy.201907` UNION ALL
  SELECT *, 'ht' AS geo_code, 'Haiti' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_ht.201907` UNION ALL
  SELECT *, 'hn' AS geo_code, 'Honduras' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_hn.201907` UNION ALL
  SELECT *, 'hk' AS geo_code, 'Hong Kong' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_hk.201907` UNION ALL
  SELECT *, 'hu' AS geo_code, 'Hungary' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_hu.201907` UNION ALL
  SELECT *, 'is' AS geo_code, 'Iceland' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_is.201907` UNION ALL
  SELECT *, 'in' AS geo_code, 'India' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_in.201907` UNION ALL
  SELECT *, 'id' AS geo_code, 'Indonesia' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_id.201907` UNION ALL
  SELECT *, 'ir' AS geo_code, 'Iran (Islamic Republic of)' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_ir.201907` UNION ALL
  SELECT *, 'iq' AS geo_code, 'Iraq' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_iq.201907` UNION ALL
  SELECT *, 'ie' AS geo_code, 'Ireland' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_ie.201907` UNION ALL
  SELECT *, 'im' AS geo_code, 'Isle of Man' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_im.201907` UNION ALL
  SELECT *, 'il' AS geo_code, 'Israel' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_il.201907` UNION ALL
  SELECT *, 'it' AS geo_code, 'Italy' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_it.201907` UNION ALL
  SELECT *, 'jm' AS geo_code, 'Jamaica' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_jm.201907` UNION ALL
  SELECT *, 'jp' AS geo_code, 'Japan' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_jp.201907` UNION ALL
  SELECT *, 'je' AS geo_code, 'Jersey' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_je.201907` UNION ALL
  SELECT *, 'jo' AS geo_code, 'Jordan' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_jo.201907` UNION ALL
  SELECT *, 'kz' AS geo_code, 'Kazakhstan' AS geo, 'Asia' AS region, 'Central Asia' AS subregion FROM `chrome-ux-report.country_kz.201907` UNION ALL
  SELECT *, 'ke' AS geo_code, 'Kenya' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_ke.201907` UNION ALL
  SELECT *, 'ki' AS geo_code, 'Kiribati' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_ki.201907` UNION ALL
  SELECT *, 'kp' AS geo_code, 'Korea (Democratic People\'s Republic of)' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_kp.201907` UNION ALL
  SELECT *, 'kr' AS geo_code, 'Korea (Republic of)' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_kr.201907` UNION ALL
  SELECT *, 'kw' AS geo_code, 'Kuwait' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_kw.201907` UNION ALL
  SELECT *, 'kg' AS geo_code, 'Kyrgyzstan' AS geo, 'Asia' AS region, 'Central Asia' AS subregion FROM `chrome-ux-report.country_kg.201907` UNION ALL
  SELECT *, 'la' AS geo_code, 'Lao People\'s Democratic Republic' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_la.201907` UNION ALL
  SELECT *, 'lv' AS geo_code, 'Latvia' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_lv.201907` UNION ALL
  SELECT *, 'lb' AS geo_code, 'Lebanon' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_lb.201907` UNION ALL
  SELECT *, 'ls' AS geo_code, 'Lesotho' AS geo, 'Africa' AS region, 'Southern Africa' AS subregion FROM `chrome-ux-report.country_ls.201907` UNION ALL
  SELECT *, 'lr' AS geo_code, 'Liberia' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_lr.201907` UNION ALL
  SELECT *, 'ly' AS geo_code, 'Libya' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_ly.201907` UNION ALL
  SELECT *, 'li' AS geo_code, 'Liechtenstein' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_li.201907` UNION ALL
  SELECT *, 'lt' AS geo_code, 'Lithuania' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_lt.201907` UNION ALL
  SELECT *, 'lu' AS geo_code, 'Luxembourg' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_lu.201907` UNION ALL
  SELECT *, 'mo' AS geo_code, 'Macao' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_mo.201907` UNION ALL
  SELECT *, 'mk' AS geo_code, 'Macedonia (the former Yugoslav Republic of)' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_mk.201907` UNION ALL
  SELECT *, 'mg' AS geo_code, 'Madagascar' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_mg.201907` UNION ALL
  SELECT *, 'mw' AS geo_code, 'Malawi' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_mw.201907` UNION ALL
  SELECT *, 'my' AS geo_code, 'Malaysia' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_my.201907` UNION ALL
  SELECT *, 'mv' AS geo_code, 'Maldives' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_mv.201907` UNION ALL
  SELECT *, 'ml' AS geo_code, 'Mali' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_ml.201907` UNION ALL
  SELECT *, 'mt' AS geo_code, 'Malta' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_mt.201907` UNION ALL
  SELECT *, 'mh' AS geo_code, 'Marshall Islands' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_mh.201907` UNION ALL
  SELECT *, 'mq' AS geo_code, 'Martinique' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_mq.201907` UNION ALL
  SELECT *, 'mr' AS geo_code, 'Mauritania' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_mr.201907` UNION ALL
  SELECT *, 'mu' AS geo_code, 'Mauritius' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_mu.201907` UNION ALL
  SELECT *, 'yt' AS geo_code, 'Mayotte' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_yt.201907` UNION ALL
  SELECT *, 'mx' AS geo_code, 'Mexico' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_mx.201907` UNION ALL
  SELECT *, 'fm' AS geo_code, 'Micronesia (Federated States of)' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_fm.201907` UNION ALL
  SELECT *, 'md' AS geo_code, 'Moldova (Republic of)' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_md.201907` UNION ALL
  SELECT *, 'mc' AS geo_code, 'Monaco' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_mc.201907` UNION ALL
  SELECT *, 'mn' AS geo_code, 'Mongolia' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_mn.201907` UNION ALL
  SELECT *, 'me' AS geo_code, 'Montenegro' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_me.201907` UNION ALL
  SELECT *, 'ms' AS geo_code, 'Montserrat' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_ms.201907` UNION ALL
  SELECT *, 'ma' AS geo_code, 'Morocco' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_ma.201907` UNION ALL
  SELECT *, 'mz' AS geo_code, 'Mozambique' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_mz.201907` UNION ALL
  SELECT *, 'mm' AS geo_code, 'Myanmar' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_mm.201907` UNION ALL
  SELECT *, 'na' AS geo_code, 'Namibia' AS geo, 'Africa' AS region, 'Southern Africa' AS subregion FROM `chrome-ux-report.country_na.201907` UNION ALL
  SELECT *, 'nr' AS geo_code, 'Nauru' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_nr.201907` UNION ALL
  SELECT *, 'np' AS geo_code, 'Nepal' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_np.201907` UNION ALL
  SELECT *, 'nl' AS geo_code, 'Netherlands' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_nl.201907` UNION ALL
  SELECT *, 'nc' AS geo_code, 'New Caledonia' AS geo, 'Oceania' AS region, 'Melanesia' AS subregion FROM `chrome-ux-report.country_nc.201907` UNION ALL
  SELECT *, 'nz' AS geo_code, 'New Zealand' AS geo, 'Oceania' AS region, 'Australia and New Zealand' AS subregion FROM `chrome-ux-report.country_nz.201907` UNION ALL
  SELECT *, 'ni' AS geo_code, 'Nicaragua' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_ni.201907` UNION ALL
  SELECT *, 'ne' AS geo_code, 'Niger' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_ne.201907` UNION ALL
  SELECT *, 'ng' AS geo_code, 'Nigeria' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_ng.201907` UNION ALL
  SELECT *, 'nf' AS geo_code, 'Norfolk Island' AS geo, 'Oceania' AS region, 'Australia and New Zealand' AS subregion FROM `chrome-ux-report.country_nf.201907` UNION ALL
  SELECT *, 'mp' AS geo_code, 'Northern Mariana Islands' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_mp.201907` UNION ALL
  SELECT *, 'no' AS geo_code, 'Norway' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_no.201907` UNION ALL
  SELECT *, 'om' AS geo_code, 'Oman' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_om.201907` UNION ALL
  SELECT *, 'pk' AS geo_code, 'Pakistan' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_pk.201907` UNION ALL
  SELECT *, 'pw' AS geo_code, 'Palau' AS geo, 'Oceania' AS region, 'Micronesia' AS subregion FROM `chrome-ux-report.country_pw.201907` UNION ALL
  SELECT *, 'ps' AS geo_code, 'Palestine, State of' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_ps.201907` UNION ALL
  SELECT *, 'pa' AS geo_code, 'Panama' AS geo, 'Americas' AS region, 'Central America' AS subregion FROM `chrome-ux-report.country_pa.201907` UNION ALL
  SELECT *, 'pg' AS geo_code, 'Papua New Guinea' AS geo, 'Oceania' AS region, 'Melanesia' AS subregion FROM `chrome-ux-report.country_pg.201907` UNION ALL
  SELECT *, 'py' AS geo_code, 'Paraguay' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_py.201907` UNION ALL
  SELECT *, 'pe' AS geo_code, 'Peru' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_pe.201907` UNION ALL
  SELECT *, 'ph' AS geo_code, 'Philippines' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_ph.201907` UNION ALL
  SELECT *, 'pl' AS geo_code, 'Poland' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_pl.201907` UNION ALL
  SELECT *, 'pt' AS geo_code, 'Portugal' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_pt.201907` UNION ALL
  SELECT *, 'pr' AS geo_code, 'Puerto Rico' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_pr.201907` UNION ALL
  SELECT *, 'qa' AS geo_code, 'Qatar' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_qa.201907` UNION ALL
  SELECT *, 're' AS geo_code, 'Réunion' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_re.201907` UNION ALL
  SELECT *, 'ro' AS geo_code, 'Romania' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_ro.201907` UNION ALL
  SELECT *, 'ru' AS geo_code, 'Russian Federation' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_ru.201907` UNION ALL
  SELECT *, 'rw' AS geo_code, 'Rwanda' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_rw.201907` UNION ALL
  SELECT *, 'bl' AS geo_code, 'Saint Barthélemy' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_bl.201907` UNION ALL
  SELECT *, 'sh' AS geo_code, 'Saint Helena, Ascension and Tristan da Cunha' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_sh.201907` UNION ALL
  SELECT *, 'kn' AS geo_code, 'Saint Kitts and Nevis' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_kn.201907` UNION ALL
  SELECT *, 'lc' AS geo_code, 'Saint Lucia' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_lc.201907` UNION ALL
  SELECT *, 'mf' AS geo_code, 'Saint Martin (French part)' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_mf.201907` UNION ALL
  SELECT *, 'pm' AS geo_code, 'Saint Pierre and Miquelon' AS geo, 'Americas' AS region, 'Northern America' AS subregion FROM `chrome-ux-report.country_pm.201907` UNION ALL
  SELECT *, 'vc' AS geo_code, 'Saint Vincent and the Grenadines' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_vc.201907` UNION ALL
  SELECT *, 'ws' AS geo_code, 'Samoa' AS geo, 'Oceania' AS region, 'Polynesia' AS subregion FROM `chrome-ux-report.country_ws.201907` UNION ALL
  SELECT *, 'sm' AS geo_code, 'San Marino' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_sm.201907` UNION ALL
  SELECT *, 'st' AS geo_code, 'Sao Tome and Principe' AS geo, 'Africa' AS region, 'Middle Africa' AS subregion FROM `chrome-ux-report.country_st.201907` UNION ALL
  SELECT *, 'sa' AS geo_code, 'Saudi Arabia' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_sa.201907` UNION ALL
  SELECT *, 'sn' AS geo_code, 'Senegal' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_sn.201907` UNION ALL
  SELECT *, 'rs' AS geo_code, 'Serbia' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_rs.201907` UNION ALL
  SELECT *, 'sc' AS geo_code, 'Seychelles' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_sc.201907` UNION ALL
  SELECT *, 'sl' AS geo_code, 'Sierra Leone' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_sl.201907` UNION ALL
  SELECT *, 'sg' AS geo_code, 'Singapore' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_sg.201907` UNION ALL
  SELECT *, 'sx' AS geo_code, 'Sint Maarten (Dutch part)' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_sx.201907` UNION ALL
  SELECT *, 'sk' AS geo_code, 'Slovakia' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_sk.201907` UNION ALL
  SELECT *, 'si' AS geo_code, 'Slovenia' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_si.201907` UNION ALL
  SELECT *, 'sb' AS geo_code, 'Solomon Islands' AS geo, 'Oceania' AS region, 'Melanesia' AS subregion FROM `chrome-ux-report.country_sb.201907` UNION ALL
  SELECT *, 'so' AS geo_code, 'Somalia' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_so.201907` UNION ALL
  SELECT *, 'za' AS geo_code, 'South Africa' AS geo, 'Africa' AS region, 'Southern Africa' AS subregion FROM `chrome-ux-report.country_za.201907` UNION ALL
  SELECT *, 'ss' AS geo_code, 'South Sudan' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_ss.201907` UNION ALL
  SELECT *, 'es' AS geo_code, 'Spain' AS geo, 'Europe' AS region, 'Southern Europe' AS subregion FROM `chrome-ux-report.country_es.201907` UNION ALL
  SELECT *, 'lk' AS geo_code, 'Sri Lanka' AS geo, 'Asia' AS region, 'Southern Asia' AS subregion FROM `chrome-ux-report.country_lk.201907` UNION ALL
  SELECT *, 'sd' AS geo_code, 'Sudan' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_sd.201907` UNION ALL
  SELECT *, 'sr' AS geo_code, 'Suriname' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_sr.201907` UNION ALL
  SELECT *, 'sj' AS geo_code, 'Svalbard and Jan Mayen' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_sj.201907` UNION ALL
  SELECT *, 'sz' AS geo_code, 'Swaziland' AS geo, 'Africa' AS region, 'Southern Africa' AS subregion FROM `chrome-ux-report.country_sz.201907` UNION ALL
  SELECT *, 'se' AS geo_code, 'Sweden' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_se.201907` UNION ALL
  SELECT *, 'ch' AS geo_code, 'Switzerland' AS geo, 'Europe' AS region, 'Western Europe' AS subregion FROM `chrome-ux-report.country_ch.201907` UNION ALL
  SELECT *, 'sy' AS geo_code, 'Syrian Arab Republic' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_sy.201907` UNION ALL
  SELECT *, 'tw' AS geo_code, 'Taiwan, Province of China' AS geo, 'Asia' AS region, 'Eastern Asia' AS subregion FROM `chrome-ux-report.country_tw.201907` UNION ALL
  SELECT *, 'tj' AS geo_code, 'Tajikistan' AS geo, 'Asia' AS region, 'Central Asia' AS subregion FROM `chrome-ux-report.country_tj.201907` UNION ALL
  SELECT *, 'tz' AS geo_code, 'Tanzania, United Republic of' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_tz.201907` UNION ALL
  SELECT *, 'th' AS geo_code, 'Thailand' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_th.201907` UNION ALL
  SELECT *, 'tl' AS geo_code, 'Timor-Leste' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_tl.201907` UNION ALL
  SELECT *, 'tg' AS geo_code, 'Togo' AS geo, 'Africa' AS region, 'Western Africa' AS subregion FROM `chrome-ux-report.country_tg.201907` UNION ALL
  SELECT *, 'to' AS geo_code, 'Tonga' AS geo, 'Oceania' AS region, 'Polynesia' AS subregion FROM `chrome-ux-report.country_to.201907` UNION ALL
  SELECT *, 'tt' AS geo_code, 'Trinidad and Tobago' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_tt.201907` UNION ALL
  SELECT *, 'tn' AS geo_code, 'Tunisia' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_tn.201907` UNION ALL
  SELECT *, 'tr' AS geo_code, 'Turkey' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_tr.201907` UNION ALL
  SELECT *, 'tm' AS geo_code, 'Turkmenistan' AS geo, 'Asia' AS region, 'Central Asia' AS subregion FROM `chrome-ux-report.country_tm.201907` UNION ALL
  SELECT *, 'tc' AS geo_code, 'Turks and Caicos Islands' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_tc.201907` UNION ALL
  SELECT *, 'tv' AS geo_code, 'Tuvalu' AS geo, 'Oceania' AS region, 'Polynesia' AS subregion FROM `chrome-ux-report.country_tv.201907` UNION ALL
  SELECT *, 'ug' AS geo_code, 'Uganda' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_ug.201907` UNION ALL
  SELECT *, 'ua' AS geo_code, 'Ukraine' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_ua.201907` UNION ALL
  SELECT *, 'ae' AS geo_code, 'United Arab Emirates' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_ae.201907` UNION ALL
  SELECT *, 'gb' AS geo_code, 'United Kingdom of Great Britain and Northern Ireland' AS geo, 'Europe' AS region, 'Northern Europe' AS subregion FROM `chrome-ux-report.country_gb.201907` UNION ALL
  SELECT *, 'us' AS geo_code, 'United States of America' AS geo, 'Americas' AS region, 'Northern America' AS subregion FROM `chrome-ux-report.country_us.201907` UNION ALL
  SELECT *, 'uy' AS geo_code, 'Uruguay' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_uy.201907` UNION ALL
  SELECT *, 'uz' AS geo_code, 'Uzbekistan' AS geo, 'Asia' AS region, 'Central Asia' AS subregion FROM `chrome-ux-report.country_uz.201907` UNION ALL
  SELECT *, 'vu' AS geo_code, 'Vanuatu' AS geo, 'Oceania' AS region, 'Melanesia' AS subregion FROM `chrome-ux-report.country_vu.201907` UNION ALL
  SELECT *, 've' AS geo_code, 'Venezuela (Bolivarian Republic of)' AS geo, 'Americas' AS region, 'South America' AS subregion FROM `chrome-ux-report.country_ve.201907` UNION ALL
  SELECT *, 'vn' AS geo_code, 'Viet Nam' AS geo, 'Asia' AS region, 'South-Eastern Asia' AS subregion FROM `chrome-ux-report.country_vn.201907` UNION ALL
  SELECT *, 'vg' AS geo_code, 'Virgin Islands (British)' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_vg.201907` UNION ALL
  SELECT *, 'vi' AS geo_code, 'Virgin Islands (U.S.)' AS geo, 'Americas' AS region, 'Caribbean' AS subregion FROM `chrome-ux-report.country_vi.201907` UNION ALL
  SELECT *, 'eh' AS geo_code, 'Western Sahara' AS geo, 'Africa' AS region, 'Northern Africa' AS subregion FROM `chrome-ux-report.country_eh.201907` UNION ALL
  SELECT *, 'ye' AS geo_code, 'Yemen' AS geo, 'Asia' AS region, 'Western Asia' AS subregion FROM `chrome-ux-report.country_ye.201907` UNION ALL
  SELECT *, 'zm' AS geo_code, 'Zambia' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_zm.201907` UNION ALL
  SELECT *, 'zw' AS geo_code, 'Zimbabwe' AS geo, 'Africa' AS region, 'Eastern Africa' AS subregion FROM `chrome-ux-report.country_zw.201907` UNION ALL
  SELECT *, 'xk' AS geo_code, 'Kosovo' AS geo, 'Europe' AS region, 'Eastern Europe' AS subregion FROM `chrome-ux-report.country_xk.201907`
)

SELECT
  geo,
  COUNT(0) AS websites,
  ROUND(COUNTIF(fast_fid >= .95) * 100 / COUNT(0), 2) AS pct_fast_fid,
  ROUND(COUNTIF(NOT(slow_fid >= .05) AND NOT(fast_fid >= .95)) * 100 / COUNT(0), 2) AS pct_avg_fid,
  ROUND(COUNTIF(slow_fid >= .05) * 100 / COUNT(0), 2) AS pct_slow_fid
FROM
  (
    SELECT
      geo,
      ROUND(SAFE_DIVIDE(SUM(IF(bin.start < 100, bin.density, 0)), SUM(bin.density)), 4) AS fast_fid,
      ROUND(SAFE_DIVIDE(SUM(IF(bin.start >= 100 AND bin.start < 300, bin.density, 0)), SUM(bin.density)), 4) AS avg_fid,
      ROUND(SAFE_DIVIDE(SUM(IF(bin.start >= 300, bin.density, 0)), SUM(bin.density)), 4) AS slow_fid
    FROM
      geos,
      UNNEST(experimental.first_input_delay.histogram.bin) AS bin
    GROUP BY
      origin,
      geo
  )
GROUP BY
  geo
ORDER BY
  websites * pct_fast_fid DESC
