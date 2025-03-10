# Generated by Django 4.2.11 on 2024-12-17 01:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmStructureRegistry', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
                CREATE OR REPLACE VIEW `cm_structure_registry_view` AS
                select
                    `csr`.`structure_id` AS `structure_id`,
                    `csr`.`structure_name` AS `structure_name`,
                    `csr`.`structure_type_id` AS `structure_type_id`,
                    `csr`.`solar_system_id` AS `solar_system_id`,
                    `cst`.`name` AS `structure_type`,
                    `css`.`name` AS `solar_system`,
                    `cst`.`id` AS `constellation_id`,
                    `cc`.`name` AS `constellation`,
                    `cc`.`region_id` AS `region_id`,
                    `corp`.`ticker` AS `corporation`,
                    `corp`.`corporation_id` AS `corporation_id`,
                    `ca`.`ticker` AS `alliance`,
                    `ca`.`alliance_id` AS `alliance_id`,
                    `fit`.`fit_json` AS `fit_json`,
                    `fit`.`modified_date` AS `fit_last_updated_date`,
                    `ee`.`character_name` AS `fit_last_updated_by`,
                    `csr`.`vulnerability` AS `vulnerability`,
                    `tmr`.`timer_datetime` AS `timer_datetime`,
                    (case
                        when (`csr`.`removed_date` is not null) then 'REMOVED'
                        else coalesce(`tmr`.`timer_type_name`, '')
                    end) AS `timer_type`,
                    `csr`.`removed_date` AS `removed_date`
                from
                    ((((((((`cm_structure_registry` `csr`
                join `cm_timer_structure_type` `cst` on
                    ((`cst`.`id` = `csr`.`structure_type_id`)))
                join `cm_solar_system` `css` on
                    ((`css`.`id` = `csr`.`solar_system_id`)))
                join `cm_constellation` `cc` on
                    ((`cc`.`id` = `css`.`constellation_id`)))
                join `cm_corporation` `corp` on
                    ((`corp`.`corporation_id` = `csr`.`corporation_id`)))
                left join `cm_alliance` `ca` on
                    ((`ca`.`alliance_id` = `corp`.`alliance_id`)))
                left join `cm_structure_registry_fit` `fit` on
                    ((`fit`.`structure_id` = `csr`.`structure_id`)))
                left join `eveonline_evecharacter` `ee` on
                    ((`ee`.`character_id` = `fit`.`character_id`)))
                left join (
                    select
                        `cct`.`timer_datetime` AS `timer_datetime`,
                        `ctt`.`name` AS `timer_type_name`,
                        `cct`.`structure_id`,
                        ROW_NUMBER() OVER(PARTITION BY `cct`.`structure_id` order by `cct`.`timer_datetime`) as `row_num`
                    from
                        `cm_corp_timer` `cct`
                    join `cm_timer_type` `ctt` on `ctt`.`id` = `cct`.`timer_type_id`
                    where (`cct`.`timer_datetime` > UTC_TIMESTAMP())
                    	) `tmr` on `tmr`.`structure_id` = `csr`.`structure_id` and `tmr`.`row_num` = 1
                    );
            """,
            reverse_sql="DROP VIEW `cm_structure_registry_view`;"
        ),
    ]
