# 웹 JavaScript 함수 참조

[참조 목차](README.md) · [브라우저 코드 설명](../../src/ccs/README.md)

Python 파일 안에 문자열로 들어 있는 **이름 있는 JavaScript 함수 100개**의 선언 위치입니다. Python AST 함수 목록과 별개입니다.

이 목록은 `function 이름(...)`과 이름에 할당한 arrow function 선언을 찾습니다. 익명 이벤트 callback과 객체 method를 모두 나열한 JavaScript AST 그래프는 아닙니다. 클릭/입력/주기 갱신의 전체 연결은 [웹 화면 구조](../ARCHITECTURE.md#web-flow)와 각 파일 설명을 함께 보세요.

<a id="module-studio_script"></a>
## `studio_script.py`에 포함된 JavaScript

| 함수 | 입력 | 선언 형태 | 소스 위치 |
|---|---|---|---|
| `$` | `id` | 이름에 할당한 arrow function | [L6](../../src/ccs/studio_script.py#L6) |
| `t` | `k` | 이름에 할당한 arrow function | [L22](../../src/ccs/studio_script.py#L22) |
| `loc` | `v` | 이름에 할당한 arrow function | [L23](../../src/ccs/studio_script.py#L23) |
| `scenarioInfo` | `f` | 이름에 할당한 arrow function | [L24](../../src/ccs/studio_script.py#L24) |
| `scenarioText` | `f,key` | 이름에 할당한 arrow function | [L25](../../src/ccs/studio_script.py#L25) |
| `scenarioName` | `f` | 이름에 할당한 arrow function | [L26](../../src/ccs/studio_script.py#L26) |
| `fieldName` | `f` | 이름에 할당한 arrow function | [L27](../../src/ccs/studio_script.py#L27) |
| `statusName` | `s` | 이름에 할당한 arrow function | [L28](../../src/ccs/studio_script.py#L28) |
| `analysisSummary` | `headline` | 이름에 할당한 arrow function | [L36](../../src/ccs/studio_script.py#L36) |
| `active` | `` | 이름에 할당한 arrow function | [L37](../../src/ccs/studio_script.py#L37) |
| `knownRun` | `id` | 이름에 할당한 arrow function | [L38](../../src/ccs/studio_script.py#L38) |
| `number` | `v` | 이름에 할당한 arrow function | [L39](../../src/ccs/studio_script.py#L39) |
| `seconds` | `v` | 이름에 할당한 arrow function | [L40](../../src/ccs/studio_script.py#L40) |
| `stringValue` | `v` | 이름에 할당한 arrow function | [L41](../../src/ccs/studio_script.py#L41) |
| `humanValue` | `value` | function 선언 | [L42](../../src/ccs/studio_script.py#L42) |
| `element` | `tag,text,className` | function 선언 | [L43](../../src/ccs/studio_script.py#L43) |
| `button` | `text,fn,className='text-button small'` | function 선언 | [L44](../../src/ccs/studio_script.py#L44) |
| `badge` | `status` | function 선언 | [L45](../../src/ccs/studio_script.py#L45) |
| `toast` | `keyOrMessage,error=false` | function 선언 | [L46](../../src/ccs/studio_script.py#L46) |
| `api` | `path,body` | function 선언 | [L47](../../src/ccs/studio_script.py#L47) |
| `mutate` | `path,body,notice` | function 선언 | [L48](../../src/ccs/studio_script.py#L48) |
| `renderScenarios` | `` | function 선언 | [L49](../../src/ccs/studio_script.py#L49) |
| `setLanguage` | `value` | function 선언 | [L50](../../src/ccs/studio_script.py#L50) |
| `selectTab` | `name` | function 선언 | [L51](../../src/ccs/studio_script.py#L51) |
| `initialize` | `data` | function 선언 | [L52](../../src/ccs/studio_script.py#L52) |
| `selectRunControls` | `` | function 선언 | [L53](../../src/ccs/studio_script.py#L53) |
| `selectRun` | `id,tab='results'` | function 선언 | [L54](../../src/ccs/studio_script.py#L54) |
| `updateMonitor` | `` | function 선언 | [L55](../../src/ccs/studio_script.py#L55) |
| `librarySummary` | `kind` | function 선언 | [L56](../../src/ccs/studio_script.py#L56) |
| `renderLibrary` | `` | function 선언 | [L57](../../src/ccs/studio_script.py#L57) |
| `openLibrary` | `kind` | function 선언 | [L58](../../src/ccs/studio_script.py#L58) |
| `runTiming` | `run` | function 선언 | [L59](../../src/ccs/studio_script.py#L59) |
| `renderHistory` | `` | function 선언 | [L60](../../src/ccs/studio_script.py#L60) |
| `renderConsole` | `` | function 선언 | [L64](../../src/ccs/studio_script.py#L64) |
| `refreshConsole` | `` | function 선언 | [L66](../../src/ccs/studio_script.py#L66) |
| `options` | `` | function 선언 | [L67](../../src/ccs/studio_script.py#L67) |
| `startRun` | `event` | function 선언 | [L68](../../src/ccs/studio_script.py#L68) |
| `addDocument` | `kind` | function 선언 | [L69](../../src/ccs/studio_script.py#L69) |
| `upload` | `kind` | function 선언 | [L70](../../src/ccs/studio_script.py#L70) |
| `changeDelay` | `value` | function 선언 | [L71](../../src/ccs/studio_script.py#L71) |
| `scenarioChanged` | `` | function 선언 | [L72](../../src/ccs/studio_script.py#L72) |
| `networkKey` | `` | function 선언 | [L73](../../src/ccs/studio_script.py#L73) |
| `refreshNetwork` | `` | function 선언 | [L74](../../src/ccs/studio_script.py#L74) |
| `updateValue` | `key,value` | function 선언 | [L75](../../src/ccs/studio_script.py#L75) |
| `networkRows` | `target,rows,kind` | function 선언 | [L76](../../src/ccs/studio_script.py#L76) |
| `renderNetwork` | `` | function 선언 | [L77](../../src/ccs/studio_script.py#L77) |
| `loadAnalysis` | `id,showLoading=true` | function 선언 | [L82](../../src/ccs/studio_script.py#L82) |
| `metric` | `label,value,unit,description` | function 선언 | [L83](../../src/ccs/studio_script.py#L83) |
| `renderAnalysis` | `` | function 선언 | [L84](../../src/ccs/studio_script.py#L84) |
| `renderEpisode` | `ep` | function 선언 | [L90](../../src/ccs/studio_script.py#L90) |
| `format` | `value` | 이름에 할당한 arrow function | [L91](../../src/ccs/studio_script.py#L91) |

<a id="module-monitor"></a>
## `monitor.py`에 포함된 JavaScript

| 함수 | 입력 | 선언 형태 | 소스 위치 |
|---|---|---|---|
| `$` | `id` | 이름에 할당한 arrow function | [L311](../../src/ccs/monitor.py#L311) |
| `asText` | `v` | 이름에 할당한 arrow function | [L312](../../src/ccs/monitor.py#L312) |
| `escapeSearch` | `v` | 이름에 할당한 arrow function | [L313](../../src/ccs/monitor.py#L313) |
| `addEvents` | `items` | function 선언 | [L314](../../src/ccs/monitor.py#L314) |
| `time` | `v` | function 선언 | [L315](../../src/ccs/monitor.py#L315) |
| `elapsed` | `start,end` | function 선언 | [L316](../../src/ccs/monitor.py#L316) |
| `terminal` | `status` | function 선언 | [L317](../../src/ccs/monitor.py#L317) |
| `filtered` | `` | function 선언 | [L318](../../src/ccs/monitor.py#L318) |
| `renderHeader` | `` | function 선언 | [L319](../../src/ccs/monitor.py#L319) |
| `populateEpisodes` | `` | function 선언 | [L320](../../src/ccs/monitor.py#L320) |
| `renderCards` | `` | function 선언 | [L321](../../src/ccs/monitor.py#L321) |
| `renderLog` | `` | function 선언 | [L322](../../src/ccs/monitor.py#L322) |
| `renderDetail` | `` | function 선언 | [L323](../../src/ccs/monitor.py#L323) |
| `renderResults` | `` | function 선언 | [L324](../../src/ccs/monitor.py#L324) |
| `render` | `` | function 선언 | [L325](../../src/ccs/monitor.py#L325) |
| `poll` | `` | function 선언 | [L326](../../src/ccs/monitor.py#L326) |
| `$` | `id` | 이름에 할당한 arrow function | [L405](../../src/ccs/monitor.py#L405) |
| `asText` | `v` | 이름에 할당한 arrow function | [L406](../../src/ccs/monitor.py#L406) |
| `terminal` | `s` | 이름에 할당한 arrow function | [L407](../../src/ccs/monitor.py#L407) |
| `searchText` | `v` | 이름에 할당한 arrow function | [L408](../../src/ccs/monitor.py#L408) |
| `eventEpoch` | `v` | 이름에 할당한 arrow function | [L409](../../src/ccs/monitor.py#L409) |
| `communicationOf` | `e` | 이름에 할당한 arrow function | [L410](../../src/ccs/monitor.py#L410) |
| `endpoint` | `id,c` | 이름에 할당한 arrow function | [L411](../../src/ccs/monitor.py#L411) |
| `messageKind` | `c` | 이름에 할당한 arrow function | [L412](../../src/ccs/monitor.py#L412) |
| `communicationText` | `e` | function 선언 | [L413](../../src/ccs/monitor.py#L413) |
| `postMonitorHeight` | `` | function 선언 | [L415](../../src/ccs/monitor.py#L415) |
| `addEvents` | `items` | function 선언 | [L425](../../src/ccs/monitor.py#L425) |
| `time` | `value` | function 선언 | [L432](../../src/ccs/monitor.py#L432) |
| `filtered` | `` | function 선언 | [L436](../../src/ccs/monitor.py#L436) |
| `runFinished` | `` | function 선언 | [L442](../../src/ccs/monitor.py#L442) |
| `routeStages` | `event` | function 선언 | [L443](../../src/ccs/monitor.py#L443) |
| `openOperations` | `` | function 선언 | [L459](../../src/ccs/monitor.py#L459) |
| `staleOperationIds` | `` | function 선언 | [L471](../../src/ccs/monitor.py#L471) |
| `renderHeader` | `` | function 선언 | [L481](../../src/ccs/monitor.py#L481) |
| `populateEpisodes` | `` | function 선언 | [L498](../../src/ccs/monitor.py#L498) |
| `renderTopology` | `` | function 선언 | [L506](../../src/ccs/monitor.py#L506) |
| `selectLatest` | `predicate` | function 선언 | [L523](../../src/ccs/monitor.py#L523) |
| `chooseEvent` | `event` | function 선언 | [L532](../../src/ccs/monitor.py#L532) |
| `renderTimeline` | `` | function 선언 | [L536](../../src/ccs/monitor.py#L536) |
| `renderDetail` | `` | function 선언 | [L565](../../src/ccs/monitor.py#L565) |
| `render` | `` | function 선언 | [L593](../../src/ccs/monitor.py#L593) |
| `poll` | `` | function 선언 | [L596](../../src/ccs/monitor.py#L596) |
| `pick` | `` | 이름에 할당한 arrow function | [L612](../../src/ccs/monitor.py#L612) |
| `pick` | `` | 이름에 할당한 arrow function | [L613](../../src/ccs/monitor.py#L613) |

<a id="module-monitor_i18n"></a>
## `monitor_i18n.py`에 포함된 JavaScript

| 함수 | 입력 | 선언 형태 | 소스 위치 |
|---|---|---|---|
| `t` | `key` | function 선언 | [L51](../../src/ccs/monitor_i18n.py#L51) |
| `eventText` | `event,field` | function 선언 | [L52](../../src/ccs/monitor_i18n.py#L52) |
| `statusText` | `status` | function 선언 | [L53](../../src/ccs/monitor_i18n.py#L53) |
| `applyMonitorLanguage` | `` | function 선언 | [L54](../../src/ccs/monitor_i18n.py#L54) |
| `setMonitorLanguage` | `value` | function 선언 | [L60](../../src/ccs/monitor_i18n.py#L60) |
