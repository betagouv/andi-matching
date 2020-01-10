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
        CASE e.naf
            {naf_rules}
        END AS score_naf,
        -- crit size ---------------------------------------------
        CASE e.taille
            {size_rules}
        END AS score_size,
        -- crit welcome ------------------------------------------
        CASE
            WHEN e.pmsmp_interest THEN 3
            WHEN (e.pmsmp_interest) AND (e.pmsmp_count_recent > 0) THEN 5
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
ORDER BY score_total DESC, distance ASC
LIMIT 100;
'''


'''
WITH comp_pos AS (
    SELECT
        id_internal,
        commune,
        earth_distance(ll_to_earth(%(lat)s, %(lon)s), ll_to_earth(lat, lon))
            AS dist
    FROM
        entreprises
    WHERE
        earth_box(ll_to_earth(%(lat)s, %(lon)s), %(dist)s * 1000) @> ll_to_earth(lat, lon)
    ORDER BY earth_box(ll_to_earth(%(lat)s, %(lon)s), %(dist)s * 1000) @> ll_to_earth(lat, lon) ASC
    {limit_test}
    ), crit_geo AS (
    -- crit geo ----------------------------------------------
    SELECT
        id_internal,
        dist,
        4 - NTILE(3) OVER(
            ORDER BY dist ASC
        ) AS score
    FROM comp_pos
    ORDER BY dist ASC
    ), crit_size AS (
    -- crit size ---------------------------------------------
    SELECT
        comp_pos.id_internal,
        {size_rules}
    FROM comp_pos
    INNER JOIN
        entreprises e ON e.id_internal = comp_pos.id_internal
    ), crit_naf AS (
    -- crit naf ----------------------------------------------
    SELECT
        comp_pos.id_internal,
        {naf_rules}
    FROM comp_pos
    INNER JOIN
        entreprises e ON e.id_internal = comp_pos.id_internal
    ), crit_welcome AS (
    -- crit welcome ------------------------------------------
    SELECT
        comp_pos.id_internal,
        CASE
            WHEN e.pmsmp_interest THEN 2
            WHEN (e.pmsmp_interest) AND (e.pmsmp_count_recent > 0) THEN 3
            ELSE 1
        END AS score
    FROM comp_pos
    INNER JOIN
        entreprises e ON e.id_internal = comp_pos.id_internal
    ), crit_contact AS (
    -- crit contact ------------------------------------------
    SELECT
        comp_pos.id_internal,
        CASE
            WHEN (COALESCE(cc.email_official, '') <> '')
            OR (COALESCE(cc.contact_1_phone, '') <> '')
            OR (COALESCE(cc.contact_2_phone, '') <> '') THEN 2
            WHEN (COALESCE(cc.contact_1_mail, '') <> '')
            OR (COALESCE(cc.contact_2_mail, '') <> '') THEN 3
            ELSE 1
        END AS score
    FROM comp_pos
    INNER JOIN
        entreprises cc ON cc.id_internal = comp_pos.id_internal
    )
SELECT
    e.id_internal as id,
    e.nom AS nom,
    e.taille AS taille,
    e.naf AS naf,
    naf.intitule_de_la_naf_rev_2 AS sector,
    array_to_string(ARRAY[
        e.phone_official_1,
        e.phone_official_2], ', ') AS phone_official,
    array_to_string(ARRAY[
        e.contact_1_phone,
        e.contact_2_phone], ', ') AS phone_contact,
    e.email_official as email_official,
    array_to_string(ARRAY[
        e.contact_1_mail,
        e.contact_2_mail], ', ') as email_contact,
    e.pmsmp_interest as pmsmp_interest,
    round(cr_ge.dist/1000) || ' km' AS distance,
    e.label as adresse,
    e.commune as commune,
    e.departement as departement,
    e.siret AS siret,
    cr_nf.score AS score_naf,
    cr_wc.score AS score_welcome,
    cr_cn.score AS score_contact,
    cr_si.score AS score_size,
    cr_ge.score AS score_geo,
    cr_ge.score * %(mul_geo)s +
    cr_si.score * %(mul_siz)s +
    cr_cn.score * %(mul_con)s +
    cr_wc.score * %(mul_wel)s +
    cr_nf.score * %(mul_naf)s AS score_total
FROM
    crit_geo cr_ge
INNER JOIN
    crit_size cr_si ON cr_si.id_internal = cr_ge.id_internal
INNER JOIN
    crit_naf cr_nf ON cr_nf.id_internal = cr_ge.id_internal
INNER JOIN
    crit_welcome cr_wc ON cr_wc.id_internal = cr_ge.id_internal
INNER JOIN
    crit_contact cr_cn ON cr_cn.id_internal = cr_ge.id_internal
INNER JOIN
    entreprises e ON e.id_internal = cr_ge.id_internal
LEFT JOIN
    naf ON e.naf = naf.sous_classe_a_732
ORDER BY score_total DESC
LIMIT 100

'''
