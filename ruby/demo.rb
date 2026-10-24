require 'json'
require 'net/http'
require 'uri'

begin
  action, value, cursor = ARGV.map { |argument| argument.dup.force_encoding(Encoding::UTF_8) }
  raise 'Use create/get/records/cancel and a value.' unless value
  base = ENV.fetch('SOCAI_API_BASE_URL').sub(%r{/$}, '')
  headers = { 'Authorization' => "Bearer #{ENV.fetch('SOCAI_API_KEY')}", 'Content-Type' => 'application/json' }
  method, path, body = 'GET', '/responses', nil
  if action == 'create'
    headers['Idempotency-Key'] = ENV.fetch('SOCAI_IDEMPOTENCY_KEY')
    raise 'Set a stable SOCAI_IDEMPOTENCY_KEY.' if headers['Idempotency-Key'].empty?
    method = 'POST'
    body = JSON.generate(model: 'socai-research', background: true, input: value)
  else
    raise 'Use a Response ID returned by create.' unless value.match?(/\Aresp_[A-Za-z0-9_-]+\z/)
    path += "/#{value}"
    case action
    when 'get'
    when 'records'
      query = { limit: 20 }
      query[:cursor] = cursor if cursor
      path += '/records?' + URI.encode_www_form(query)
    when 'cancel'
      method, path = 'POST', path + '/cancel'
    else
      raise 'Use create, get, records or cancel.'
    end
  end
  uri = URI(base + path)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = uri.scheme == 'https'
  http.open_timeout = http.read_timeout = http.write_timeout = 30
  http.max_retries = 0
  request = (method == 'POST' ? Net::HTTP::Post : Net::HTTP::Get).new(uri, headers)
  request.body = body if body
  response = http.request(request)
  raise "HTTP #{response.code}; request ID: #{response['X-Request-ID']}" unless response.is_a?(Net::HTTPSuccess)
  puts response.body
rescue StandardError => error
  warn error.message.gsub(ENV['SOCAI_API_KEY'].to_s.empty? ? '__missing_key__' : ENV['SOCAI_API_KEY'], '[redacted]')
  exit 1
end
