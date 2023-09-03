import scrapy


class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  start_urls = ['https://pokemondb.net/pokedex/all']

  def parse(self, response):
    rows = response.css('table#pokedex > tbody > tr')
    for row in rows:
      link = row.css("td:nth-child(2) > a::attr(href)")
      yield response.follow(link.get(), self.parse_pokemon)

  def parse_pokemon(self, response):
    name = response.css('h1::text')
    number = response.css(
      'table.vitals-table > tbody > tr:nth-child(1) > td > strong::text')
    height = response.css(
      'table.vitals-table > tbody > tr:nth-child(4) > td::text')
    weight = response.css(
      'table.vitals-table > tbody > tr:nth-child(5) > td::text')
    type = response.css('th:contains("Type") + td a::text').getall()

    pokemon_types = [t.strip() for t in type]

    evolution = response.css(
      'h2:contains("Evolution chart") + div.infocard-list-evo > div.infocard')

    next_evolutions = []
    for element in evolution:
      poke_num = element.css('small::text').get()
      poke_name = element.css('a.ent-name::text').get()
      poke_url = element.css('a.ent-name::attr(href)').get()
      next_evolutions.append({
        'Number': poke_num,
        'Name': poke_name,
        'URL': poke_url
      })

    ability_links = response.css(
      'table.vitals-table > tbody > tr:nth-child(6) td a::attr(href)').getall(
      )

    for ability_link in ability_links:
      yield response.follow(ability_link,
                            self.parse_ability,
                            meta={
                              'Number': number.get(),
                              'Page URL': response.url,
                              'Name': name.get(),
                              'Next Evolutions': next_evolutions,
                              'Height': height.get(),
                              'Weight': weight.get(),
                              'Types': pokemon_types,
                            })

  def parse_ability(self, response):
    ability_name = response.css('h1::text')
    ability_description = response.selector.xpath(
      "//div[@class='grid-col span-md-12 span-lg-6']/p/text()")

    yield {
      'Number': response.meta['Number'],
      'Page URL': response.meta['Page URL'],
      'Name': response.meta['Name'],
      'Next Evolutions': response.meta['Next Evolutions'],
      'Height': response.meta['Height'],
      'Weight': response.meta['Weight'],
      'Types': response.meta['Types'],
      'Ability': {
        'Name': ability_name.get(),
        'URL': response.url,
        'Effect Description': ability_description.extract()
      }
    }
