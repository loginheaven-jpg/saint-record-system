/**
 * 성도기록부 시스템 Backend API
 * 
 * 기능:
 * 1. ID 생성 (LockService 사용하여 동시성 제어)
 * 2. 트랜잭션이 필요한 데이터 처리
 */

/**
 * 새로운 ID 생성 (동시성 안전)
 * @param {string} seqName - 시퀀스 이름 (member_id, family_id 등)
 * @returns {string} 새로운 ID
 */
function generateId(seqName) {
  const lock = LockService.getScriptLock();
  
  try {
    // 30초 대기 후 락 획득 실패 시 예외
    lock.waitLock(30000);
    
    // _Sequences 시트 접근
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('_Sequences');
    if (!sheet) {
      throw new Error('_Sequences sheet not found');
    }
    
    const data = sheet.getDataRange().getValues();
    
    // 헤더: seq_name, last_value, prefix, padding
    let rowIndex = -1;
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === seqName) {
        rowIndex = i;
        break;
      }
    }
    
    if (rowIndex === -1) {
      throw new Error('Unknown sequence: ' + seqName);
    }
    
    // 현재 값 읽기 (0-based index applied to data array)
    // data[rowIndex][1] is last_value
    const lastValue = Number(data[rowIndex][1]);
    const prefix = data[rowIndex][2];
    const padding = Number(data[rowIndex][3]);
    
    // 새 값 계산
    const newValue = lastValue + 1;
    
    // 시트 업데이트 (1-based row/col index for getRange)
    // Row: rowIndex + 1 (header) + 1 (0-index correction) -> rowIndex + 1 is actually the row number in 0-based data? No.
    // data[0] is header (Row 1). data[1] is Row 2.
    // So if rowIndex is 1, it matches Row 2.
    sheet.getRange(rowIndex + 1, 2).setValue(newValue);
    
    // ID 문자열 생성
    const newId = prefix + String(newValue).padStart(padding, '0');
    
    return newId;
    
  } catch (e) {
    Logger.log('Error generating ID: ' + e.toString());
    throw e;
  } finally {
    lock.releaseLock();
  }
}

/**
 * 성도 ID 생성
 */
function generateMemberId() {
  return generateId('member_id');
}

/**
 * 가정 ID 생성
 */
function generateFamilyId() {
  return generateId('family_id');
}

/**
 * 신앙이력 ID 생성
 */
function generateEventId() {
  return generateId('event_id');
}

/**
 * Web API 엔드포인트 (GET)
 */
function doGet(e) {
  const action = e.parameter.action;
  
  let result;
  
  try {
    switch(action) {
      case 'generateMemberId':
        result = { success: true, id: generateMemberId() };
        break;
      case 'generateFamilyId':
        result = { success: true, id: generateFamilyId() };
        break;
      case 'generateEventId':
        result = { success: true, id: generateEventId() };
        break;
      case 'ping':
        result = { success: true, message: 'pong' };
        break;
      default:
        result = { success: false, error: 'Unknown action: ' + action };
    }
  } catch (error) {
    result = { success: false, error: error.toString() };
  }
  
  return ContentService
    .createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * 테스트용 함수
 */
function testGenerateId() {
  Logger.log(generateMemberId());
}
