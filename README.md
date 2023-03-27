# TargetData Challenge

Desafio lançado como parte do processo seletivo para Desenvolvedor Back-End na empresa Targetdata

### Instalação com Docker (Recommended)

```
docker-compose up
```

Agora pode visitar http://localhost:5000

## ToDo
- [x] Crie um banco de dados MongoDB em Docker. 
  
- [x] Crie um ElasticSearch em Docker. 
  
- [x] Crie uma API utilizando Flask e Python. 
  
- [x] Crie um endpoint na sua api para criar usuário e senha e salvar no mongoDB. 
  
- [x] Crie outro endpoint na sua api para criar um access token. 
  
- [x] Crie um endpoint na sua api com o método “POST” com um campo CEP requirido, onde será consultado o endereço usando o CEP na api da ViaCEP (https://viacep.com.br/) e pegar a cidade retornada e buscar a previsão do tempo dos 4 dias dessa cidade na api do INPE (http://servicos.cptec.inpe.br/XML/). OBS: A sua api deve retornar todos os campos da ViaCEP e do INPE juntos em JSON. 

- [x] Crie logs de todas as requisições feita na sua api e salve no ElasticSearch. 

- [x] Crie um endpoint na sua api com o método “GET” para trazer todos os logs do usuário. 
  
- [x] Crie um arquivo Dockfile e docker-compose.yaml para rodar o container da api. 

## Demo

https://user-images.githubusercontent.com/72797625/228084728-26bf257b-090b-4665-9f8e-3c080f8cd71a.mp4


