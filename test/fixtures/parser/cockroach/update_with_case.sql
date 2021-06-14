UPDATE t1
SET a  =
        CASE
            WHEN c IN ('Type1', 'Type2', 'Type3', 'Type4',
                          'Type5') THEN 'FREEBNORT'
            WHEN c IN ('Type6', 'Type7') THEN 'UMMAGUMMA'
            WHEN c IN ('Type8', 'Type9') THEN 'WAGAMAMA'
            ELSE NULL END,

    b =
        CASE
            WHEN c IN ('Type1', 'Type2') THEN 'DINGBATS'
            WHEN c IN ('Type3', 'Type4', 'Type5') THEN 'HURDLES'
            WHEN c IN ('Type6') THEN 'DISCUS'
            WHEN c IN ('Type7') THEN 'BEANBAGS'
            WHEN c IN ('Type8', 'Type9') THEN 'BOVVERED'
            ELSE NULL END;


