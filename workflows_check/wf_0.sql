select 
    wf_to_start,
    to_char(min(start_time), 'HH24:MI') as start_time,
    to_char(max(end_time), 'HH24:MI') as finish_time,
    --max(run_err_code) ,
    max(run_status_code)
from 
(
select 
COALESCE (wfname, '') || COALESCE ('[', '')  || COALESCE (runinst_name, '') || COALESCE (']', '')  as wf_to_start
 ,start_time  
,end_time
 ,run_err_code
 , run_status_code
  from  
     (  
     select   v.runinst_name  ,
        (
        select s.subj_name from infarep_r70p_1.opb_subject s where s.subj_id =r.subject_id
        ) subjname  
        ,  
        (
        select t.task_name from infarep_r70p_1.opb_task t where t.task_id = r.workflow_id and rownum =1
        ) wfname  
        , r.* 
        from  infarep_r70p_1.opb_task_inst_run r   left join infarep_r70p_1.opb_wflow_run v  on r.workflow_run_id = v.workflow_run_id  
        where   1=1
     ) s
where 1=1
and wfname = '%s'
and runinst_name  = '%s'
and to_char(start_time, 'DD-MON-YY') = to_char(CURRENT_DATE, 'DD-MON-YY')
)  t
group by wf_to_start
