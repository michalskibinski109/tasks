from datetime import datetime
from logging import Logger, getLogger
import sqlite3
from pydantic import BaseModel
import requests


class Product(BaseModel):
    product_id: str
    variant_id: str
    stock_id: int
    supply: str


class ProcessDataAction:
    def __init__(
        self,
        logger: Logger = getLogger(),
        url="https://dummy.server/products/example?id=",
    ) -> None:
        self.logger = logger
        self.server_communicator = ServerCommunicator(url=url, logger=logger)
        self.database_connector = DatabaseConnector(logger=logger)

    def create_products_list(self, json_data: dict) -> list[Product]:
        products = []
        for supply in json_data["details"]["supply"]:
            product_supply = self.__get_supply(supply)
            product = Product(
                product_id=json_data["id"],
                variant_id=supply["variant_id"],
                stock_id=1,
                supply=product_supply,
            )
            products.append(product)
        return products

    def __get_supply(self, product_data: dict) -> int:
        supply = sum(
            stock["quantity"]
            for stock in product_data["stock_data"]
            if stock["stock_id"] == 1
        )
        return supply

    def create_product_from_bundle(self, json_data: dict) -> list[Product]:
        self.logger.info("Bundle loaded")
        # Get the minimum supply of the products in the bundle
        min_supply = self.__get_min_supply(json_data)
        self.logger.debug(f"Found {len(json_data['bundle_items'])} products")
        product = Product(
            product_id=json_data["id"],
            variant_id=None,
            stock_id=1,
            supply=min_supply,
        )
        return [product]

    def __get_min_supply(self, json_data: dict) -> int:
        for product_id in json_data["bundle_items"]:
            product_data = self.get_data_from_server(product_id)
            for supply in product_data["details"]["supply"]:
                self.logger.debug(f"Supply: {supply}")
                supply = self.__get_supply(supply)
                self.logger.debug(f"Supply: {supply}")
                min_supply = min(min_supply, supply)
        return min_supply

    def __call__(self, procuct_ids: list) -> None:
        for product_id in procuct_ids:
            product_data = self.server_communicator.get_product(product_id)
            if product_data["type"] != "bundle":
                products = self.create_product_list(product_data)
            else:
                products = self.create_product_from_bundle(product_data)
            for product in products:
                self.database_connector.insert_product(product)
            self.logger.info(f"Process for {product_id} finished")


class ServerCommunicator:
    def __init__(
        self,
        logger: Logger = getLogger(),
        url: str = "https://dummy.server/products/example?id=",
    ) -> None:
        self.logger = logger
        self.url = url

    def get_product(self, product_id: int) -> dict:
        response = requests.get(self.url + str(product_id))
        response.raise_for_status()
        response_json = (
            response.json()
        )  # I am using json instead of content So we can access the data as dict.
        self.logger.info(f"Data downloaded from server {len(response_json)}")
        self.__validate_response_json(response_json)
        return response_json

    def __validate_response_json(self, response_json: dict) -> None:
        if response_json.get("type") and response_json["type"] == "bundle":
            return
        try:
            response_json["id"]
            response_json["details"]["supply"][0]["variant_id"]
            response_json["details"]["supply"][0]["stock_data"][0]["quantity"]
        except KeyError as err:
            self.logger.error(f"Invalid response content: {err}")
            raise err


class DatabaseConnector:
    def __init__(self, logger: Logger, database="database.sqlite") -> None:
        self.logger = logger
        self.database = database
        self.con = sqlite3.connect(self.database)
        self.cursor = self.con.cursor()

    def insert_product(self, product: Product) -> None:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(
                f"INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES"
                f"({time}, {product.product_id}, {product.variant_id}, {product.stock_id}, {product.supply})"
            )
        except sqlite3.Error as err:
            self.logger.error(f"Error: {err}")
            raise err
        self.logger.info("Data saved to database")


if __name__ == "__main__":
    model = ProcessDataAction()
    model([-2, -3])  # Let's assume that negative numbers are valid xd.
