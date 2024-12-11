import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd

# 엑셀 파일 로드
try:
    excel_file = "C:\\Users\\Name_Oing\\Desktop\\개발튤\capto\\actions\\home_shopping_data.xlsx"
    product_df = pd.read_excel(excel_file, sheet_name="상품 정보")
    stock_df = pd.read_excel(excel_file, sheet_name="재고 현황")
    price_df = pd.read_excel(excel_file, sheet_name="가격 정보")
except Exception as e:
    logging.error(f"Failed to load Excel file: {str(e)}")

class ActionStockInfo(Action):
    def name(self) -> Text:
        return "action_stock_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            product = tracker.get_slot("product")
            if product:
                product_info = product_df[product_df["상품명"].str.contains(product, case=False, na=False)]
                if not product_info.empty:
                    product_id = product_info.iloc[0]["상품ID"]
                    stock_info = stock_df[stock_df["상품ID"] == product_id]
                    if not stock_info.empty:
                        response = f"{product}의 재고 현황입니다:\n"
                        for _, row in stock_info.iterrows():
                            response += f"사이즈: {row['사이즈']}, 색상: {row['색상']}, 재고: {row['재고수량']}개\n"
                    else:
                        response = f"죄송합니다. {product}의 재고 정보를 찾을 수 없습니다."
                else:
                    response = f"죄송합니다. {product}에 대한 정보를 찾을 수 없습니다."
            else:
                response = "죄송합니다. 어떤 상품에 대해 문의하시는지 알 수 없습니다."
            
            dispatcher.utter_message(text=response)
        except Exception as e:
            logging.error(f"Error in action_stock_info: {str(e)}")
            dispatcher.utter_message(text="죄송합니다. 재고 정보를 처리하는 중에 오류가 발생했습니다.")
        return []

class ActionColorInfo(Action):
    def name(self) -> Text:
        return "action_color_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            product = tracker.get_slot("product")
            if product:
                product_info = product_df[product_df["상품명"].str.contains(product, case=False, na=False)]
                if not product_info.empty:
                    colors = product_info.iloc[0]["색상"]
                    response = f"{product}의 색상 정보입니다: {colors}"
                else:
                    response = f"죄송합니다. {product}에 대한 정보를 찾을 수 없습니다."
            else:
                response = "죄송합니다. 어떤 상품에 대해 문의하시는지 알 수 없습니다."
            
            dispatcher.utter_message(text=response)
        except Exception as e:
            logging.error(f"Error in action_color_info: {str(e)}")
            dispatcher.utter_message(text="죄송합니다. 색상 정보를 처리하는 중에 오류가 발생했습니다.")
        return []

class ActionSizeInfo(Action):
    def name(self) -> Text:
        return "action_size_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            product = tracker.get_slot("product")
            if product:
                product_info = product_df[product_df["상품명"].str.contains(product, case=False, na=False)]
                if not product_info.empty:
                    sizes = product_info.iloc[0]["사이즈"]
                    response = f"{product}의 사이즈 정보입니다: {sizes}"
                else:
                    response = f"죄송합니다. {product}에 대한 정보를 찾을 수 없습니다."
            else:
                response = "죄송합니다. 어떤 상품에 대해 문의하시는지 알 수 없습니다."
            
            dispatcher.utter_message(text=response)
        except Exception as e:
            logging.error(f"Error in action_size_info: {str(e)}")
            dispatcher.utter_message(text="죄송합니다. 사이즈 정보를 처리하는 중에 오류가 발생했습니다.")
        return []

class ActionPriceInfo(Action):
    def name(self) -> Text:
        return "action_price_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            product = tracker.get_slot("product")
            if product:
                product_info = product_df[product_df["상품명"].str.contains(product, case=False, na=False)]
                if not product_info.empty:
                    product_id = product_info.iloc[0]["상품ID"]
                    price_info = price_df[price_df["상품ID"] == product_id]
                    if not price_info.empty:
                        price = price_info.iloc[0]["가격"]
                        response = f"{product}의 가격은 {price}원입니다."
                    else:
                        response = f"죄송합니다. {product}의 가격 정보를 찾을 수 없습니다."
                else:
                    response = f"죄송합니다. {product}에 대한 정보를 찾을 수 없습니다."
            else:
                response = "죄송합니다. 어떤 상품에 대해 문의하시는지 알 수 없습니다."
            
            dispatcher.utter_message(text=response)
        except Exception as e:
            logging.error(f"Error in action_price_info: {str(e)}")
            dispatcher.utter_message(text="죄송합니다. 가격 정보를 처리하는 중에 오류가 발생했습니다.")
        return []
    

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="죄송합니다. 요청하신 정보를 이해하지 못했습니다. 다시 시도해 주세요.")
        return []