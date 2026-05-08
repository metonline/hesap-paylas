<?php
// PHP Upload Handler - script.js yüklemek için
// URL: http://hesappaylas.com/upload-handler.php

header('Content-Type: application/json');

try {
    // JSON verisi al
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);
    
    if (!$data) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid JSON']);
        exit;
    }
    
    $content = isset($data['content']) ? $data['content'] : '';
    
    if (empty($content)) {
        http_response_code(400);
        echo json_encode(['error' => 'No content provided']);
        exit;
    }
    
    // Dosya yolunu belirle
    $file_path = __DIR__ . '/script.js';
    
    // Dosyayı yaz
    $bytes_written = file_put_contents($file_path, $content);
    
    if ($bytes_written === false) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to write file']);
        exit;
    }
    
    // Başarı yanıtı
    http_response_code(200);
    echo json_encode([
        'success' => true,
        'message' => 'script.js updated successfully',
        'bytes' => $bytes_written
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
