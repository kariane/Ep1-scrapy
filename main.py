import scrapy


class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  start_urls = ['https://pokemondb.net/pokedex/all']

  def parse(self, response):
    linhas = response.css('table#pokedex > tbody > tr')
    for linha in linhas:
      link = linha.css("td:nth-child(2) > a::attr(href)")
      yield response.follow(link.get(), self.parser_pokemon)

  def parser_pokemon(self, response):
    nome = response.css('h1::text')
    numero = response.css(
      'table.vitals-table > tbody > tr:nth-child(1) > td > strong::text')
    altura = response.css(
      'table.vitals-table > tbody > tr:nth-child(4) > td::text')
    peso = response.css(
      'table.vitals-table > tbody > tr:nth-child(5) > td::text')
    tipo = response.css('th:contains("Type") + td a::text').getall()

    pokemon_tipos = [t.strip() for t in tipo]

    evolucao = response.css(
      'h2:contains("Evolution chart") + div.infocard-list-evo > div.infocard')

    proximas_evolucoes = []
    for element in evolucao:
      poke_num = element.css('small::text').get()
      poke_nome = element.css('a.ent-name::text').get()
      poke_url = element.css('a.ent-name::attr(href)').get()
      proximas_evolucoes.append({
        'Numero': poke_num,
        'Nome': poke_nome,
        'URL': poke_url
      })

    habilidade_links = response.css(
      'table.vitals-table > tbody > tr:nth-child(6) td a::attr(href)').getall(
      )

    for link_habilidade in habilidade_links:
      yield response.follow(link_habilidade,
                            self.parser_habilidade,
                            meta={
                              'Numero': numero.get(),
                              'URL da Pagina': response.url,
                              'Nome': nome.get(),
                              'Proximas Evolucoes': proximas_evolucoes,
                              'Altura': altura.get(),
                              'Peso': peso.get(),
                              'Tipos': pokemon_tipos,
                            })

  def parser_habilidade(self, response):
    nome_habilidade = response.css('h1::text')
    descricao_efeito = response.selector.xpath(
      "//div[@class='grid-col span-md-12 span-lg-6']/p/text()")

    yield {
      'Numero': response.meta['Numero'],
      'URL da Pagina': response.meta['URL da Pagina'],
      'Nome': response.meta['Nome'],
      'Proximas Evolucoes': response.meta['Proximas Evolucoes'],
      'Altura': response.meta['Altura'],
      'Peso': response.meta['Peso'],
      'Tipos': response.meta['Tipos'],
      'Habilidade': {
        'Nome': nome_habilidade.get(),
        'URL': response.url,
        'Descricao Efeito': descricao_efeito.extract()
      }
    }
