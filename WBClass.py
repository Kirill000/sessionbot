# from wb_api import WBApi
from typing import List
import requests
from config import config

class WB:
  
  def __init__(self, token):
    # api = WBApi(api_key=token)
    # self.api=api
    self.token=token
    try:
      self.warehouses_info = self.get_warehouses()
      self.warehouses_names = self.get_warehouses_names()
    except:
      pass
    
  def check_connection(self):
    
    url = 'https://common-api.wildberries.ru/ping'
    
    headers = {
      "Authorization": self.token
    }
    
    try:
      response = requests.get(url, headers=headers).json()
    except:
      return (False, "JSON unpack error")

    if "Status" in response:
      return (True, response["Status"])
    else:
      return (False, response["title"])    
    
  def get_acceptance_indexes(self, warehouse_ids:List[int]=None):
    '''
    Метод для получения коэффициентов приемки по всем складам
    '''
    
    url = 'https://supplies-api.wildberries.ru/api/v1/acceptance/coefficients'
        
    headers = {
      "Authorization": self.token
    }
    
    params = {}
    
    if warehouse_ids != None:
      
      warehouseIDs = ""
      for id in warehouse_ids:
        warehouseIDs += (str(id))+","
      
      params = {
        'warehouseIDs': warehouseIDs[:-1]
      }
      
    response = requests.get(url, headers=headers, params=params)
    
    return response.json()
  
  def pack_acceptance_indexes(self):
    indexes = self.get_acceptance_indexes() #check for errors
    pack_dict = {}
    try:
      for i in indexes:
        if not i["warehouseName"] in pack_dict:  
          warehouseName = i["warehouseName"]
          boxTypeName = i["boxTypeName"]
          del i["warehouseName"]
          del i["boxTypeName"]
          pack_dict[warehouseName] = {boxTypeName: [i]}
        else:
          warehouseName = i["warehouseName"]
          del i["warehouseName"]
          
          if not i["boxTypeName"] in pack_dict[warehouseName]:
            boxTypeName = i["boxTypeName"]
            del i["boxTypeName"]
            pack_dict[warehouseName][boxTypeName] = [i]
          else:
            boxTypeName = i["boxTypeName"]
            del i["boxTypeName"]
            pack_dict[warehouseName][boxTypeName].append(i)
    except Exception as error:
      print(error)
    
    return pack_dict
  
  def compare_acceptance_indexes(self, indexes1, indexes2):
    updates = []
    new_storages = []
    
    if indexes1 != indexes2:
      new_storages = list(indexes2.keys())
      for i1, k1 in zip(indexes1.values(), indexes1.keys()):
        try:
          i2 = indexes2[k1]
          new_storages.remove(k1)
          if i1 != i2:
            for box_type_coefficient_for_date1, box_type1 in zip(i1.values(), i1.keys()):
              box_type_coefficient_for_date2 = i2[box_type1]
              for date_dict1, date_dict2 in zip(box_type_coefficient_for_date1, box_type_coefficient_for_date2):
                if date_dict1["coefficient"] != date_dict2["coefficient"] and (date_dict1["date"] == date_dict2["date"]):
                  
                  if date_dict2["coefficient"] == -1:
                    coef = "Поставки временно недоступны"
                  else:
                    coef = "Коэффициент: "+str(date_dict2["coefficient"])
                    
                  updates.append("<b>Поступило новое обновление!</b>\n"+"Дата: "+str(date_dict2["date"])+"\n"+"Склад: "+k1+"\n"+"Тара: "+box_type1+"\n"+coef+"\n")
        except Exception as error:
          print(error)
          
    if len(new_storages) != 0:
      for storage in new_storages:
        strings = "<b>Новая информация по складу "+str(storage)+"</b>\n"
        for indexes_types, indexes_types_key in zip(indexes2[storage].values(), indexes2[storage].keys()): 
          accessible_coefficients = False
          for index_type in indexes_types:
            
            cur_coef_acc = False
            if index_type["coefficient"] == -1:
              coef = "Поставки временно недоступны"
            else:
              coef = "Коэффициент: "+str(index_type["coefficient"])
              if not accessible_coefficients:
                strings+="Тара: "+indexes_types_key+":\n"
              accessible_coefficients = True
              cur_coef_acc = True
            
            if cur_coef_acc:
              strings+=str(index_type["date"])+": "+coef+"\n"
        if accessible_coefficients and (not strings in config.RECENT_STORAGES_UPDATES.values()):
          updates.append(strings)
          config.RECENT_STORAGES_UPDATES[storage] = strings

    if len(updates) != 0 and updates != config.COEFFICIENT_UPDATES:
      return updates
    else:
      return None
    
  def get_warehouses(self):
    
    url = "https://supplies-api.wildberries.ru/api/v1/warehouses"
    
    headers = {
      "Authorization": self.token
    }
    
    response = requests.get(url, headers=headers)

    return response.json()
  
  def get_warehouses_names(self):
    try:
      warehouse_names = []
      for wh in self.warehouses_info:
        warehouse_names.append(wh["name"])
      return warehouse_names
    except Exception as error:
      print(error)
      return None