WITH organizations AS (

    SELECT
        id,
        organization_key
    FROM {{ ref('platform_stg__organizations') }}

),

accounts AS (

SELECT
        app_key,
        organization_id
    FROM {{ ref('platform_stg__accounts') }}

),

owners_packages AS (

    SELECT
        owner_id,
        owner_type,
        package_id,
        created_at,
        updated_at,
        started_at
    FROM {{ ref('platform_stg__owners_packages') }}

),

owner_packages_organization_app AS (

    SELECT
        accounts.app_key AS store_id,
        package_id,
        owners_packages.created_at,
        owners_packages.updated_at,
        owners_packages.started_at
    FROM owners_packages
    INNER JOIN organizations
        ON organizations.organization_key = owner_id
    INNER JOIN accounts
        ON accounts.organization_id = organizations.id
    WHERE LOWER(owner_type) = 'organization' AND app_key IS NOT NULL
),

owner_packages_app AS (

    SELECT
        owner_id AS store_id,
        package_id,
        created_at,
        updated_at,
        started_at
    FROM owners_packages
    WHERE LOWER(owner_type) = 'store'
),

owner_packages_store_view AS (

    SELECT
        store_id,
        package_id,
        created_at,
        updated_at,
        started_at
    FROM owner_packages_organization_app
    UNION ALL
    SELECT
        store_id,
        package_id,
        created_at,
        updated_at,
        started_at
    FROM owner_packages_app
)

SELECT * FROM owner_packages_store_view
