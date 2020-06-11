MATCH_QUERY = '''
SELECT
    id_internal AS id,
    nom,
    adresse,
    siret,
    taille,
    naf,
    sector,
    commune,
    departement,
    phone_official_1 as phonenumber,
    adresse,
    round(prm.dist::NUMERIC/1000, 1) AS distance,
    prm.lat AS lat,
    prm.lon AS lon,
    prm.siret AS siret,
    score_naf,
    score_welcome,
    score_contact,
    score_size,
    score_geo,
    (   score_geo * %(mul_geo)s +
        score_size * %(mul_siz)s +
        score_contact * %(mul_con)s +
        score_welcome * %(mul_wel)s +
        score_naf * %(mul_naf)s
    )
    AS score_total
FROM
   (
   SELECT
        id_internal,
        nom,
        lat,
        lon,
        siret,
        commune,
        label as adresse,
        departement,
        phone_official_1,
        naf,
        taille,
        naf.intitule_de_la_naf_rev_2 AS sector,
        ST_Distance(geom, orig_geom)
            AS dist,
        -- crit geo ---------------------------------------------
        6 - NTILE(5) OVER(
            ORDER BY ST_Distance(geom, orig_geom) ASC
        ) AS score_geo,
        -- crit naf ----------------------------------------------
        {naf_rules}
        AS score_naf,
        -- crit size ---------------------------------------------
        CASE e.taille
            {size_rules}
        END AS score_size,
        -- crit welcome ------------------------------------------
        CASE
            WHEN (e.pmsmp_interest) AND (e.boe) THEN 5
            WHEN e.boe THEN 4
            WHEN (e.pmsmp_interest) AND (e.pmsmp_count_recent > 0) THEN 3
            WHEN e.pmsmp_interest  THEN 2
            ELSE 1
        END AS score_welcome,
        -- crit contact ------------------------------------------
        CASE
            WHEN (COALESCE(e.email_official, '') <> '')
            OR (COALESCE(e.contact_1_phone, '') <> '')
            OR (COALESCE(e.contact_2_phone, '') <> '') THEN 3
            WHEN (COALESCE(e.contact_1_mail, '') <> '')
            OR (COALESCE(e.contact_2_mail, '') <> '') THEN 5
            ELSE 1
        END AS score_contact
    FROM
        entreprises e
    LEFT JOIN
        naf ON e.naf = naf.sous_classe_a_732
    CROSS JOIN
        (SELECT ST_MakePoint(%(lon)s, %(lat)s)::geography AS orig_geom) AS r
    WHERE
        ST_DWithin(geom, orig_geom, %(dist)s * 1000)
    ORDER BY dist ASC
    {limit_test}
    ) AS prm
WHERE
    -- Filter results, leave only those who are somewhat related to what's been asked
    score_naf > 1
ORDER BY score_total DESC, distance ASC
LIMIT 100;
'''

MATCH_QUERY_PSYPG2 = '''
    -- see github history
'''
