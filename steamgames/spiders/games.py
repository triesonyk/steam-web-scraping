import scrapy

cookies = {'birthtime':'568022401','mature_content': '1'}

class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/search']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=cookies, callback=self.parse)

    def remove_characters(self, value):
        try:
            cleaned = value.replace('\r', '')
            cleaned = cleaned.replace('\t', '')
            cleaned = cleaned.replace('\n', '')
        except:
            cleaned = None
        return cleaned

    def remove_characters_list(self, value_list):
        cleaned_list = []
        try:
            for value in value_list:
                cleaned = value.replace('\r', '')
                cleaned = cleaned.replace('\t', '')
                cleaned = cleaned.replace('\n', '')
                cleaned_list.append(cleaned)
        except:
            cleaned_list = None
        return cleaned_list

    def get_platforms(self, list_classes):
        platforms = []
        for item in list_classes:
            platform = item.split(' ')[-1]
            if platform == 'win':
                platforms.append('Windows')
            if platform == 'mac':
                platforms.append('Mac OS')
            if platform == 'linux':
                platforms.append('Linux')
            if platform == 'vr_supported':
                platforms.append('VR Supported')
        return platforms

    def parse(self, response):    
        games = response.xpath('//div[@id="search_resultsRows"]/a')
        for game in games:
            title = game.xpath('.//span[@class="title"]/text()').get()
            game_url = game.xpath('.//@href').get()
            img = game.xpath('.//div[@class="col search_capsule"]/img/@src').get()
            release_date = game.xpath('.//div[@class="col search_released responsive_secondrow"]/text()').get()
            platforms = self.get_platforms(game.xpath('.//span[contains(@class, "platform_img") or @class="vr_supported"]/@class').getall())
            reviews = game.xpath('.//span[contains(@class, "search_review_summary")]/@data-tooltip-html').get()
            discount_rate = game.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()').get()
            original_price = game.xpath('normalize-space(.//div[@class="col search_price  responsive_secondrow"]/text() | .//div[@class="col search_price discounted responsive_secondrow"]/span/strike/text())').get()
            discounted_price = game.xpath('normalize-space(.//div[@class="col search_price discounted responsive_secondrow"]/text()[2])').get()
            yield response.follow(
                url=game_url,
                callback=self.parse_game,
                meta={
                    'title' : title,
                    'url' : game_url,
                    'image' : img,
                    'release_date' : release_date,
                    'platforms' : platforms,
                    'reviews' : reviews,
                    'discount_rate' : discount_rate,
                    'original_price' : original_price,
                    'discounted_price' : discounted_price 
                }
            )
        next_page = response.xpath('//div[@class="search_pagination_right"]/a[text()=">"]/@href').get()
        if next_page:
            yield scrapy.Request(
                    url=next_page,
                    callback=self.parse
                )

    def parse_game(self,response):
        title = response.request.meta['title']
        game_url = response.request.meta['url']
        img = response.request.meta['image']
        release_date = response.request.meta['release_date']
        platforms = response.request.meta['platforms']
        discount_rate = response.request.meta['discount_rate']
        original_price = response.request.meta['original_price']
        discounted_price = response.request.meta['discounted_price']
        developer = response.xpath('//div[@id="developers_list"]/a/text()').getall()
        publisher = response.xpath('//div[@class="glance_ctn_responsive_left"]/div[@class="dev_row"][2]/div/a/text()').getall()
        overall_reviews = response.xpath('(//div[@id="userReviews"]/div/div/span[contains(@class,"game_review_summary")])[1]/text()').get()
        text_reviews = self.remove_characters(response.xpath('(//span[@class="nonresponsive_hidden responsive_reviewdesc"])[1]/text()').get())
        description = self.remove_characters(response.xpath('//div[@class="game_description_snippet"]/text()').get())
        tags = self.remove_characters_list(response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').getall())
        processor = response.xpath('(//strong[contains(text(),"Processor")])[1]/following-sibling::node()[1]').get()
        ram = response.xpath('(//strong[contains(text(),"Memory")])[1]/following-sibling::node()[1]').get()
        graphic_card = response.xpath('(//strong[contains(text(),"Graphics")])[1]/following-sibling::node()[1]').get()
        rating = response.xpath('//div[@class="game_rating_agency"]/text()').get()
        language = self.remove_characters_list(response.xpath('//td[@class="ellipsis"]/text()').getall())
        metacriticts = self.remove_characters(response.xpath('//div[@class="score high"]/text()').get())
        yield{
            'title' : title,
            'url' : game_url,
            'image' : img,
            'release_date' : release_date,
            'platforms' : platforms,
            'discount_rate' : discount_rate,
            'original_price' : original_price,
            'discounted_price' : discounted_price,
            'developer' : developer,
            'publisher' : publisher,
            'overall_reviews' : overall_reviews,
            'text_reviews' : text_reviews,
            'description' : description,
            'tags' : tags,
            'processor' : processor,
            'ram' : ram,
            'graphic_card' : graphic_card,
            'rating' : rating,
            'language' : language,
            'metacriticts' : metacriticts
        }
            


