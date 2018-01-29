LOCK ROW ACCESS

SELECT DatabaseName AS "db name"
       ,MAX(AddMaxPerm_GB) AS "GB to add"
       ,CASE WHEN SUM(Counter) = 1
             THEN 'prognoz po pikam'
             WHEN SUM(Counter) = 2
             THEN 'prognoz'
             ELSE 'both'
        END AS "type"
FROM (
        SELECT DatabaseName
               ,AddMaxPerm_GB
               ,1 AS Counter
        FROM (
                SELECT 
                   ds.DatabaseName
                  ,SUM(ds.MaxPerm)/1024**3 AS MaxPerm_GB
                  ,SUM(ds.CurrentPerm)/1024**3 AS CurPerm_GB
                  ,MAX(maxdiffds.MaxDiffPeakCur_GB) MaxDiff_GB
                  ,CurPerm_GB+MaxDiff_GB*1.1 AS PermLine
                  ,PermLine - MaxPerm_GB AS AddMaxPerm_GB
                FROM dbc.DiskSpaceV ds
                     JOIN (

                            SELECT TMP.DatabaseName
                                   ,MAX(CASE WHEN TMP.PeakPerm_GB > 0 
                                             THEN TMP.PeakPerm_GB - TMP1.CurPerm_GB 
                                             ELSE 0
                                        END) AS MaxDiffPeakCur_GB
                            FROM (

                                    SELECT
                                      h.LogDate
                                      ,h.DatabaseName
                                      ,h.CurPerm_GB
                                      ,h.MaxPerm_GB
                                      ,h.PeakPerm_GB
                                      ,MAX(h1.logdate) AS LastDate
                                    FROM 
                                         (SELECT logdate
                                                 ,UPPER(DatabaseName) AS DatabaseName
                                                 ,SUM(CurrentPerm)/1024**3 AS CurPerm_GB
                                                 ,SUM(MaxPerm)/1024**3 AS MaxPerm_GB
                                                 ,SUM(PeakPerm)/1024**3 AS PeakPerm_GB
                                          FROM PDCRDATA.DatabaseSpace_Hst 
                                          GROUP BY 1,2) h

                                         LEFT JOIN (SELECT logdate
                                                           ,UPPER(DatabaseName) AS DatabaseName
                                                    FROM PDCRDATA.DatabaseSpace_Hst 
                                                    GROUP BY 1,2) h1
                                              ON h.databasename = h1.databasename
                                              AND h.LogDate > h1.Logdate
                                    WHERE h.DatabaseName NOT IN(
                                                              SELECT TRIM(a.baza_1) 
                                                              FROM (  SELECT TRIM(ch.PARENT) AS baza_1 FROM DBC.Children ch
                                                                      WHERE ch.child LIKE ANY('%SANDBOXES%','%DATALABS%')
                                                                      UNION
                                                                      SELECT TRIM(ch.child) AS baza_1 FROM  DBC.Children ch
                                                                      WHERE ch.PARENT LIKE ANY ('%SANDBOXES%', '%DATALABS%')
                                                                   )a
                                                              WHERE a.baza_1 NOT IN ('DBC','TSA','sysdba4') 
                                                              )
                                        AND h.DatabaseName NOT IN (SELECT Child FROM dbc.Children WHERE PARENT='GRP_USR')
                                        AND h.DatabaseName NOT IN (SELECT Child FROM dbc.Children WHERE PARENT='PDCRADM')
                                        AND h.DatabaseName NOT IN 
                                                                    ('DBC'
                                                                    ,'TSA'
                                                                    ,'sysdba4'
                                                                    ,'console'
                                                                    ,'Crashdumps'
                                                                    ,'DBCEXTENSION'
                                                                    ,'dbcmngr'
                                                                    ,'LockLogShredder'

                                                                    ,'PDCRADM'
                                                                    ,'SAS_SYSFNLIB'
                                                                    ,'SBX_DB_SME_DKK_ANALYSE'
                                                                    ,'SQLJ'
                                                                    ,'Sys_Calendar'
                                                                    ,'SysAdmin'
                                                                    ,'SYSBAR'
                                                                    ,'SYSLIB'
                                                                    ,'SYSSPATIAL'
                                                                    ,'SystemFe'
                                                                    ,'SYSUDTLIB'
                                                                    ,'TD_SYSFNLIB'
                                                                    ,'TD_SYSXML'
                                                                    ,'TDQCD'
                                                                    ,'TDStats'
                                                                    ,'tdwm'
                                                                    ,'TEC_GRP_DB'
                                                                    ,'TEC_SESSION_CONTROL'
                                                                    ,'TEC_USERS_METHA'
                                                                    ,'viewpoint'
                                                                    ,'009_PVB'
                                                                    ,'015_DF'
                                                                    ,'prd3_db_tmp'
                                                                    ,'prd3_1_db_tmp'

                                                                    ,'remote_database'
                                                                    ,'SYSJDBC'
                                                                    ,'SYSUIF'
                                                                    ,'TD_SYSGPL'
                                                                    ,'temp_database'

                                                                    ,'SANDBOXES'
                                                                    ,'RcoestDB1'
                                                                    ,'TDAdmin20161102165133'
                                                                    ,'001_MIS_Retail_ARC'
                                                                    ,'012_MIS_DT_ARC'
                                                                    ,'014_DF_ARC'
                                                                    ,'016_DF_OAKB_ARC'
                                                                    ,'030_MIS_Platform_ARC'
                                                                    ,'OAKB_SBX_ARC'
                                                                    ,'SBX_ADL_2_010_DB_DWH'
                                                                    ,'SBX_ADL_2_010_VD_DWH'
                                                                    ,'External_AP'
                                                                    ,'SBX_tmp_006_oakb'

                                                                    ) 

                                        AND h.LogDate >= ADD_MONTHS(CURRENT_DATE - EXTRACT(DAY FROM CURRENT_DATE)+1, -4)
                                    GROUP BY 1,2,3,4,5
                                ) TMP
                                JOIN (SELECT logdate
                                             ,UPPER(DatabaseName) AS DatabaseName
                                             ,SUM(CurrentPerm)/1024**3 AS CurPerm_GB
                                      FROM PDCRDATA.DatabaseSpace_Hst 
                                      GROUP BY 1,2) TMP1
                                     ON TMP.DatabaseName = TMP1.DatabaseName
                                     AND TMP.LastDate = TMP1.LogDate
                            GROUP BY 1
                         ) maxdiffds
                        ON maxdiffds.DatabaseName = ds.DatabaseName
                GROUP BY 1
                HAVING PermLine > MaxPerm_GB
            ) TMP


        UNION ALL


        SELECT DatabaseName
               ,AddMaxPerm_GB
               ,2 AS Counter
        FROM (
                SELECT UPPER(h.DatabaseName) AS DatabaseName
                       ,SUM(h.CurrentPerm)/1024**3 AS CurPerm_GB
                       ,MAX(v.MaxPerm) AS MaxPerm_GB
                       ,SUM(h.PeakPerm)/1024**3 AS PeakPerm_GB
                       ,ROUND(CAST(PeakPerm_GB/MaxPerm_GB AS NUMERIC(18,4)),4) AS PermPct
                       ,ROUND(PeakPerm_GB / 0.85,2) - MaxPerm_GB AS AddMaxPerm_GB
                FROM PDCRDATA.DatabaseSpace_Hst h, (SELECT DatabaseName
                                                           ,SUM(MaxPerm)/1024**3 AS MaxPerm
                                                    FROM dbc.DiskSpaceV
                                                    GROUP BY 1) v
                WHERE h.LogDate = DATE - 1
                      AND h.DatabaseName = v.DatabaseName
                        AND h.DatabaseName NOT IN(
                                              SELECT TRIM(a.baza_1) 
                                              FROM (  SELECT TRIM(ch.PARENT) AS baza_1 FROM DBC.Children ch
                                                      WHERE ch.child LIKE ANY('%SANDBOXES%','%DATALABS%')
                                                      UNION
                                                      SELECT TRIM(ch.child) AS baza_1 FROM  DBC.Children ch
                                                      WHERE ch.PARENT LIKE ANY ('%SANDBOXES%', '%DATALABS%')
                                                   )a
                                              WHERE a.baza_1 NOT IN ('DBC','TSA','sysdba4') 
                                          )
                        AND h.DatabaseName NOT IN (SELECT Child FROM dbc.Children WHERE PARENT='GRP_USR')
                        AND h.DatabaseName NOT IN (SELECT Child FROM dbc.Children WHERE PARENT='PDCRADM')
                        AND h.DatabaseName NOT IN 
                                            ('DBC'
                                            ,'TSA'
                                            ,'sysdba4'
                                            ,'console'
                                            ,'Crashdumps'
                                            ,'DBCEXTENSION'
                                            ,'dbcmngr'
                                            ,'LockLogShredder'

                                            ,'PDCRADM'
                                            ,'SAS_SYSFNLIB'
                                            ,'SBX_DB_SME_DKK_ANALYSE'
                                            ,'SQLJ'
                                            ,'Sys_Calendar'
                                            ,'SysAdmin'
                                            ,'SYSBAR'
                                            ,'SYSLIB'
                                            ,'SYSSPATIAL'
                                            ,'SystemFe'
                                            ,'SYSUDTLIB'
                                            ,'TD_SYSFNLIB'
                                            ,'TD_SYSXML'
                                            ,'TDQCD'
                                            ,'TDStats'
                                            ,'tdwm'
                                            ,'TEC_GRP_DB'
                                            ,'TEC_SESSION_CONTROL'
                                            ,'TEC_USERS_METHA'
                                            ,'viewpoint'
                                            ,'009_PVB'
                                            ,'015_DF'
                                            ,'prd3_db_tmp'
                                            ,'prd3_1_db_tmp'

                                            ,'remote_database'
                                            ,'SYSJDBC'
                                            ,'SYSUIF'
                                            ,'TD_SYSGPL'
                                            ,'temp_database'

                                            ,'SANDBOXES'
                                            ,'RcoestDB1'
                                            ,'TDAdmin20161102165133'
                                            ,'001_MIS_Retail_ARC'
                                            ,'012_MIS_DT_ARC'
                                            ,'014_DF_ARC'
                                            ,'016_DF_OAKB_ARC'
                                            ,'030_MIS_Platform_ARC'
                                            ,'OAKB_SBX_ARC'
                                            ,'SBX_ADL_2_010_DB_DWH'
                                            ,'SBX_ADL_2_010_VD_DWH'
                                            ,'External_AP'
                                            ,'SBX_tmp_006_oakb'

                                            ) 

                GROUP BY 1
                HAVING PermPct >= 0.9
            ) TMP
    ) XXX
GROUP BY 1
ORDER BY 2 DESC;