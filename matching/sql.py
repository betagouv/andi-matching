"""
Naf rule example:
    CASE company.naf
        WHEN '3220Z' THEN 3
        WHEN '3240Z' THEN 3
        WHEN '3101Z' THEN 3
        WHEN '1629Z' THEN 3
    ELSE
        CASE substring(company.naf, 0, 3)
            WHEN '31' THEN 2
            WHEN '32' THEN 2
            WHEN '16' THEN 2
            ELSE 1
        END
    END AS score

Size rule example:
    CASE company.taille
        WHEN '3-5' THEN 2
        WHEN '6-9' THEN 3
        WHEN '10-19' THEN 3
        WHEN '20-49' THEN 3
        WHEN '50-99' THEN 3
        WHEN '100-199' THEN 3
        WHEN '200-249' THEN 2
        WHEN '250-499' THEN 2
        WHEN '500-999' THEN 2
        WHEN '1000-1999' THEN 2
        WHEN '2000-4999' THEN 2
        WHEN '5000-9999' THEN 2
        ELSE 1
    END AS score
"""

MATCH_QUERY = '''
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
    cr_ge.score * 1 +
    cr_si.score * 3 +
    cr_cn.score * 3 +
    cr_wc.score * 3 +
    cr_nf.score * 5 AS score_total
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
