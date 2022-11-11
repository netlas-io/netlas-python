import pytest
from click.testing import CliRunner
from netlas.__main__ import host, query

@pytest.fixture(scope="module")
def runner():
    return CliRunner()

def test_host(runner):
    result = runner.invoke(host, ['-f', 'json'])
    assert result.exit_code == 0
    assert '"type": "ip"' in result.output

def test_query_response(runner):
    result = runner.invoke(query, ['-f', 'json', 'port:222'])
    assert result.exit_code == 0
    assert '"port": 222' in result.output

def test_query_response_field_exclude(runner):
    result = runner.invoke(query, ['-f', 'json', '-e', 'port', 'port:222'])
    assert result.exit_code == 0
    assert '"ip": ' in result.output
    assert '"port": 222' not in result.output

def test_query_response_field_include(runner):
    result = runner.invoke(query, ['-f', 'json', '-i', 'port', 'port:222'])
    assert result.exit_code == 0
    assert '"ip": ' not in result.output
    assert '"port": 222' in result.output

def test_query_domain(runner):
    result = runner.invoke(query, ['-f', 'json', '-d', 'domain', 'domain:netlas.io'])
    assert result.exit_code == 0
    assert '"domain": "netlas.io"' in result.output

def test_query_domain_field_exclude(runner):
    result = runner.invoke(query, ['-f', 'json', '-d', 'domain', '-e', 'domain', 'domain:netlas.io'])
    assert result.exit_code == 0
    assert '"zone": "io"' in result.output
    assert '"domain": "netlas.io"' not in result.output

def test_query_domain_field_include(runner):
    result = runner.invoke(query, ['-f', 'json', '-d', 'domain', '-i', 'domain', 'domain:netlas.io'])
    assert result.exit_code == 0
    assert '"zone": "io"' not in result.output
    assert '"domain": "netlas.io"' in result.output

def test_query_whoisip(runner):
    result = runner.invoke(query, ['-f', 'json', '-d', 'whois-ip', 'ip:8.8.8.8'])
    assert result.exit_code == 0
    assert '"net": ' in result.output

def test_query_whoisip_field_exclude(runner):
    result = runner.invoke(query, ['-f', 'json', '-d', 'whois-ip', '-e', 'net', 'ip:8.8.8.8'])
    assert result.exit_code == 0
    assert '"ip": ' in result.output
    assert '"net": {' not in result.output

def test_query_whoisip_field_include(runner):
    result = runner.invoke(query, ['-f', 'json', '-d', 'whois-ip', '-i', 'net', 'ip:8.8.8.8'])
    assert result.exit_code == 0
    assert '"ip": ' not in result.output
    assert '"net": {' in result.output
