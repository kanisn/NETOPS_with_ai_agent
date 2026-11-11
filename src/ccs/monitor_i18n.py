"""Bilingual strings for the standalone activity monitor."""

SCRIPT = r"""
let monitorLanguage='ko';
try{monitorLanguage=localStorage.getItem('ccs-ui-language')||'ko'}catch{}
if(!['ko','en'].includes(monitorLanguage))monitorLanguage='ko';

const MONITOR_WORDS={
  ko:{
    eyebrow:'CCS · D0 observability',title:'NetOps Agent 활동 모니터',subtitle:'요청부터 진단·조치·검증까지 실제 event로 확인합니다.',
    checking:'상태 확인 중',live:'LIVE · 실행 중',finished:'FINISHED · 실행 종료',snapshot:'저장된 화면',disconnected:'연결 끊김',unknown:'상태 확인 중',
    runId:'실행 ID',mode:'모드',runStatus:'실행 상태',episodes:'에피소드',successful:'성공',apiCalls:'API 호출',inProgress:'진행 중',
    diagramTitle:'에이전트 처리 흐름',diagramHint:'색이 선명한 경로는 현재 실행 중이며, 선택한 기록과 같은 경로도 강조됩니다.',
    human:'운영자',operation:'운영 에이전트',diagnosis:'진단 에이전트',runbook:'Runbook 검색',memory:'Incident Memory',tools:'Network Tools',
    humanCaption:'요청과 최종 판단',operationCaption:'흐름 관리 · 변경 책임',diagnosisCaption:'근거 수집 · 조회 전용',runbookCaption:'BM25 검색',memoryCaption:'승인된 장애 기록',toolsCaption:'MCP · 역할별 권한',
    request:'요청',report:'보고',context:'컨텍스트',action:'조치',approval:'승인',inspect:'조사',evidence:'근거',conclusion:'결론',search:'검색',result:'결과',read:'조회',draft:'초안',write:'저장',preview:'미리보기',apply:'적용',verify:'검증',rollback:'롤백',
    routeRequest:'요청 전달',routeReport:'결과 보고',routeDelegate:'진단 위임',routeReturn:'진단 반환',routeRag:'Runbook 검색',routeMemory:'Memory 조회 / 저장',routeOpMcp:'MCP · 조치/검증',routeDiagMcp:'MCP · 조회 전용',routeInternal:'내부 작업',
    orderNote:'오른쪽 진행 기록은 관측 시각을 기준으로 최신순으로 표시합니다.',newestFirst:'최신순',
    allEpisodes:'모든 에피소드',allChannels:'모든 경로',allStatuses:'모든 상태',searchPlaceholder:'동작, 도구, 대상 검색',pause:'기록 일시정지',resume:'기록 다시 받기',autoOn:'최신 따라가기 켜짐',autoOff:'최신 따라가기 꺼짐',
    timeline:'진행 기록',selectedActivity:'선택한 기록',visible:'표시',emptyTimeline:'현재 필터에 맞는 기록이 없습니다.',selectActivity:'기록을 선택하면 담당 역할, 전달 경로, 입력과 결과를 확인할 수 있습니다.',
    actor:'역할 / 방향',channel:'경로',nodeStage:'Node / 단계',component:'Component',actionField:'동작',status:'상태',episode:'에피소드',operationId:'동작 ID',writerSequence:'기록자 / 순서',utc:'UTC',modeField:'모드',
    rawTitle:'원본 이벤트',rawHint:'해당 단계에 기록된 원본 필드입니다.',
    communication:'통신 경로',messageContent:'전달 항목과 내용',requestMessage:'요청',responseMessage:'응답',failedRequest:'요청 실패',internalMessage:'내부 처리',source:'출발지',destination:'목적지',protocol:'방식',
    endpoint_operation:'운영 에이전트',endpoint_diagnosis:'진단 에이전트',endpoint_human:'운영자',endpoint_tools:'Network Tools',endpoint_network:'네트워크 Backend',endpoint_runbook:'Runbook 저장소',endpoint_memory:'Memory 저장소',endpoint_model:'AI 모델',endpoint_runner:'실행 관리자',endpoint_unknown:'기록에 없음',
    oldRun:'이 run에는 activity event가 없습니다. 이전 형식의 run이거나 계측 시작 전 상태일 수 있습니다.',
    stale:'실행 종료 시 완료 event가 없는 단계',noEvents:'event 없음',seconds:'초',minutes:'분',hours:'시간',started:'시작',succeeded:'성공',failed:'실패',waiting:'대기',skipped:'생략',info:'정보',
    noTarget:'대상 정보 없음',generic:'일반 단계'
  },
  en:{
    eyebrow:'CCS · D0 observability',title:'NetOps Agent Activity Monitor',subtitle:'Follow requests, diagnosis, action, and verification through recorded events.',
    checking:'Checking status',live:'LIVE · Running',finished:'FINISHED · Complete',snapshot:'Offline snapshot',disconnected:'Connection lost',unknown:'Checking status',
    runId:'Run ID',mode:'Mode',runStatus:'Run status',episodes:'Episodes',successful:'Successful',apiCalls:'API calls',inProgress:'In progress',
    diagramTitle:'Live agent topology',diagramHint:'Bright routes are executing now; the route matching the selected log is also emphasized.',
    human:'Human Operator',operation:'Operation Agent',diagnosis:'Diagnosis Agent',runbook:'Runbooks Search',memory:'Incident Memory',tools:'Network Tools',
    humanCaption:'Intent & oversight',operationCaption:'Workflow · change owner',diagnosisCaption:'Evidence · read-only tools',runbookCaption:'BM25 retrieval',memoryCaption:'Approved incident records',toolsCaption:'MCP · role-bound access',
    request:'Request',report:'Report',context:'Context',action:'Action',approval:'Approval',inspect:'Inspect',evidence:'Evidence',conclusion:'Conclusion',search:'Search',result:'Result',read:'Read',draft:'Draft',write:'Write',preview:'Preview',apply:'Apply',verify:'Verify',rollback:'Rollback',
    routeRequest:'Request',routeReport:'Report',routeDelegate:'Delegate',routeReturn:'Return',routeRag:'Retrieval',routeMemory:'Read / Write',routeOpMcp:'MCP · change',routeDiagMcp:'MCP · read-only',routeInternal:'Internal work',
    orderNote:'Activity is shown newest first, ordered by observed time.',newestFirst:'Newest first',
    allEpisodes:'All episodes',allChannels:'All routes',allStatuses:'All statuses',searchPlaceholder:'Search actions, tools, and targets',pause:'Pause updates',resume:'Resume updates',autoOn:'Follow latest ON',autoOff:'Follow latest OFF',
    timeline:'Activity timeline',selectedActivity:'Selected activity',visible:'Visible',emptyTimeline:'No activity matches the current filters.',selectActivity:'Select an activity to inspect its role, route, actual input, and result.',
    actor:'Role / direction',channel:'Route',nodeStage:'Node / stage',component:'Component',actionField:'Action',status:'Status',episode:'Episode',operationId:'Operation ID',writerSequence:'Writer / sequence',utc:'UTC',modeField:'Mode',
    rawTitle:'Original event',rawHint:'Original fields recorded for this activity.',
    communication:'Communication',messageContent:'Transferred fields and content',requestMessage:'Request',responseMessage:'Response',failedRequest:'Request failed',internalMessage:'Internal processing',source:'Source',destination:'Destination',protocol:'Protocol',
    endpoint_operation:'Operation Agent',endpoint_diagnosis:'Diagnosis Agent',endpoint_human:'Human Operator',endpoint_tools:'Network Tools',endpoint_network:'Network Backend',endpoint_runbook:'Runbook store',endpoint_memory:'Memory store',endpoint_model:'AI model',endpoint_runner:'Runner',endpoint_unknown:'Not recorded',
    oldRun:'This run has no activity events. It may predate activity instrumentation or use an older format.',
    stale:'Stage has no terminal event at run end',noEvents:'No events',seconds:'s',minutes:'m',hours:'h',started:'Started',succeeded:'Succeeded',failed:'Failed',waiting:'Waiting',skipped:'Skipped',info:'Info',
    noTarget:'No target recorded',generic:'Generic stage'
  }
};

function t(key){return MONITOR_WORDS[monitorLanguage]?.[key]??MONITOR_WORDS.en[key]??key}
function eventText(event,field){const value=event?.presentation?.[field];return value?.[monitorLanguage]||value?.en||''}
function statusText(status){return t(status)||status}
function applyMonitorLanguage(){
  document.documentElement.lang=monitorLanguage;
  for(const element of document.querySelectorAll('[data-i18n]'))element.textContent=t(element.dataset.i18n);
  const search=document.getElementById('search');if(search)search.placeholder=t('searchPlaceholder');
  const control=document.getElementById('monitorLanguage');if(control)control.value=monitorLanguage;
}
function setMonitorLanguage(value){
  if(!['ko','en'].includes(value)||value===monitorLanguage)return;
  const windowY=window.scrollY,detail=document.getElementById('detail');
  const detailY=detail?.scrollTop||0;
  monitorLanguage=value;try{localStorage.setItem('ccs-ui-language',value)}catch{}
  render();applyMonitorLanguage();
  requestAnimationFrame(()=>{window.scrollTo(0,windowY);if(detail)detail.scrollTop=detailY;postMonitorHeight()});
}
"""
