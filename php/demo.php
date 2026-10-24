<?php
try {
    [$script, $action, $value] = $argv + [null, null, null];
    if (!$value) throw new RuntimeException('Use create/get/records/cancel and a value.');
    $env = function ($name) {
        $value = getenv($name);
        if (!$value) throw new RuntimeException("Set $name.");
        return $value;
    };
    $base = rtrim($env('SOCAI_API_BASE_URL'), '/');
    $headers = ['Authorization: Bearer ' . $env('SOCAI_API_KEY'), 'Content-Type: application/json'];
    $method = 'GET'; $path = '/responses'; $body = null;
    if ($action === 'create') {
        $headers[] = 'Idempotency-Key: ' . $env('SOCAI_IDEMPOTENCY_KEY');
        $method = 'POST';
        $body = json_encode(['model'=>'socai-research', 'background'=>true, 'input'=>$value], JSON_THROW_ON_ERROR);
    } else {
        if (!preg_match('/\Aresp_[A-Za-z0-9_-]+\z/', $value)) throw new RuntimeException('Use a Response ID returned by create.');
        $path .= '/' . $value;
        if ($action === 'records') $path .= '/records?' . http_build_query(['limit'=>20] + (isset($argv[3]) ? ['cursor'=>$argv[3]] : []));
        elseif ($action === 'cancel') { $method = 'POST'; $path .= '/cancel'; }
        elseif ($action !== 'get') throw new RuntimeException('Use create, get, records or cancel.');
    }
    $handle = curl_init($base . $path);
    curl_setopt_array($handle, [CURLOPT_CUSTOMREQUEST=>$method, CURLOPT_HTTPHEADER=>$headers, CURLOPT_RETURNTRANSFER=>true, CURLOPT_TIMEOUT=>30, CURLOPT_FOLLOWLOCATION=>false]);
    if ($body !== null) curl_setopt($handle, CURLOPT_POSTFIELDS, $body);
    $result = curl_exec($handle);
    if ($result === false) throw new RuntimeException('HTTP transport failed; creation may be uncertain. Reuse the same operation key.');
    $status = curl_getinfo($handle, CURLINFO_RESPONSE_CODE);
    curl_close($handle);
    if ($status < 200 || $status >= 300) throw new RuntimeException("HTTP $status; inspect credentials, quota and API availability.");
    echo $result, PHP_EOL;
} catch (Throwable $error) {
    fwrite(STDERR, str_replace(getenv('SOCAI_API_KEY') ?: '__missing_key__', '[redacted]', $error->getMessage()) . PHP_EOL);
    exit(1);
}
