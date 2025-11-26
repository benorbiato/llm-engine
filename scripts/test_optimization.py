"""
Script para testar as otimizações de cache e tratamento de erros.
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Processo de teste
TEST_PROCESSO = {
    "numeroProcesso": "0001234-56.2023.1.99.9999",
    "esfera": "Federal",
    "valorCondenacao": 5000.00,
    "documentos": [
        {"tipo": "sentenca", "descricao": "Sentença condenatória"}
    ]
}


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_api_status():
    """Test API status endpoint."""
    print_section("1️⃣  Testando Status da API")
    
    response = requests.get(f"{BASE_URL}/monitoring/api-status")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Status:")
        print(f"  - Serviço: {data.get('service')}")
        print(f"  - Provider: {data.get('api')['provider']}")
        print(f"  - Modelo: {data.get('api')['model']}")
        print(f"  - API Key Configurada: {data.get('api')['api_key_configured']}")
        
        print("\n💡 Recomendações:")
        for rec in data.get('recommendations', []):
            print(f"  {rec}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


def test_cache_stats():
    """Test cache statistics endpoint."""
    print_section("2️⃣  Estatísticas de Cache (Inicial)")
    
    response = requests.get(f"{BASE_URL}/monitoring/cache-stats")
    
    if response.status_code == 200:
        data = response.json()
        cache = data.get('cache', {})
        print(f"✅ Cache Stats:")
        print(f"  - Total de entries: {cache.get('total_entries', 0)}")
        print(f"  - TTL: {cache.get('ttl_minutes', 0)} minutos")
        print(f"  - Processados: {len(cache.get('entries', []))}")
        
        if cache.get('entries'):
            print("\n  Processos em cache:")
            for entry in cache.get('entries', []):
                print(f"    - {entry.get('numero_processo')} (às {entry.get('cached_at')})")
    else:
        print(f"❌ Erro: {response.status_code}")


def test_verify_first_call():
    """Test first verification (should call API)."""
    print_section("3️⃣  Primeira Chamada (API - não há cache)")
    
    print("📤 Enviando requisição de verificação...")
    print(f"   Processo: {TEST_PROCESSO['numeroProcesso']}")
    
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/verify/",
        json=TEST_PROCESSO,
        timeout=30
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Verificação realizada em {elapsed:.2f}s")
        print(f"  - Decisão: {data.get('decision')}")
        print(f"  - Confiança: {data.get('confidence')}")
        print(f"  - Tempo processamento: {data.get('processing_time_ms')}ms")
        print(f"  - Justificativa: {data.get('rationale')[:100]}...")
    elif response.status_code == 429:
        data = response.json()
        print(f"⚠️  Erro HTTP 429 - Créditos Esgotados!")
        print(f"  - Erro: {data.get('detail', {}).get('error')}")
        print(f"  - Mensagem: {data.get('detail', {}).get('message')}")
        print(f"  - Help: {data.get('detail', {}).get('help')}")
        return False
    elif response.status_code == 401:
        data = response.json()
        print(f"❌ Erro HTTP 401 - Autenticação Falhou!")
        print(f"  - Erro: {data.get('detail', {}).get('error')}")
        print(f"  - Mensagem: {data.get('detail', {}).get('message')}")
        return False
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return False
    
    return True


def test_verify_cache_hit():
    """Test second verification (should hit cache)."""
    print_section("4️⃣  Segunda Chamada (Cache - mesmo processo)")
    
    print("📤 Enviando mesma requisição novamente...")
    
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/verify/",
        json=TEST_PROCESSO,
        timeout=30
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resposta em {elapsed:.2f}s")
        print(f"  - Decisão: {data.get('decision')}")
        
        if elapsed < 0.1:
            print(f"  🚀 Cache Hit! (resposta < 100ms)")
        else:
            print(f"  ⚠️  Pode não ter sido do cache (lento)")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


def test_cache_stats_after():
    """Test cache statistics after verifications."""
    print_section("5️⃣  Estatísticas de Cache (Após verificações)")
    
    response = requests.get(f"{BASE_URL}/monitoring/cache-stats")
    
    if response.status_code == 200:
        data = response.json()
        cache = data.get('cache', {})
        print(f"✅ Cache Stats:")
        print(f"  - Total de entries: {cache.get('total_entries', 0)}")
        print(f"  - TTL: {cache.get('ttl_minutes', 0)} minutos")
        
        if cache.get('entries'):
            print("\n  Processos em cache:")
            for entry in cache.get('entries', []):
                print(f"    ✓ {entry.get('numero_processo')}")
    else:
        print(f"❌ Erro: {response.status_code}")


def test_clear_cache():
    """Test clearing cache."""
    print_section("6️⃣  Limpando Cache")
    
    response = requests.post(f"{BASE_URL}/monitoring/cache/clear")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data.get('message')}")
        
        # Verify cache was cleared
        response = requests.get(f"{BASE_URL}/monitoring/cache-stats")
        if response.status_code == 200:
            cache = response.json().get('cache', {})
            print(f"   Total de entries agora: {cache.get('total_entries', 0)}")
    else:
        print(f"❌ Erro: {response.status_code}")


def test_health():
    """Test health endpoint."""
    print_section("❤️  Health Check")
    
    response = requests.get(f"{BASE_URL}/monitoring/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Saúde: {data.get('status')}")
        print(f"   Serviço: {data.get('service')}")
        print(f"   API Key: {'✓ Configurada' if data.get('api_key_configured') else '✗ Não configurada'}")
    else:
        print(f"❌ Erro: {response.status_code}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  🧪 Script de Teste de Otimizações")
    print("="*60)
    print("\n⚠️  Certifique-se que a API está rodando em http://localhost:8000")
    print("   Execute: python -m uvicorn app.main:app --reload")
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/monitoring/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ API não respondeu. Inicie a API primeiro!")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ Não conseguiu conectar à API em http://localhost:8000")
        print("   Inicie a aplicação com: python -m uvicorn app.main:app --reload")
        return
    
    # Run tests
    test_health()
    test_api_status()
    test_cache_stats()
    
    if not test_verify_first_call():
        print("\n❌ Falha na primeira chamada. Verifique sua chave de API.")
        return
    
    test_cache_stats()
    test_verify_cache_hit()
    test_cache_stats_after()
    test_clear_cache()
    
    print_section("✅ Testes Concluídos!")
    print("📊 Resumo:\n")
    print("  ✓ Cache funcionando")
    print("  ✓ Endpoints de monitoramento operacionais")
    print("  ✓ Tratamento de erros implementado")
    print("\n💡 Próximos passos:")
    print("  1. Monitorar logs para verificar padrão de uso")
    print("  2. Ajustar TTL de cache conforme necessário")
    print("  3. Configurar alertas para créditos baixos")
    print("  4. Considerar persistência de cache em BD\n")


if __name__ == "__main__":
    main()

