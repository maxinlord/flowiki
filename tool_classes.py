from datetime import datetime
import os
from pprint import pprint
import random
import string
from init_db import flow_db
import qrcode


class Model:
    def __init__(self, id_user) -> None:
        self.id_user = id_user

    @staticmethod
    def _create_tag(len_tag: int = 8):
        signs = string.digits + string.ascii_letters
        tag = "".join(random.choices(signs, k=len_tag))
        return tag

    @staticmethod
    def _wrap_num(
        num,
        q_signs_after_comma: int = 2,
        format: str = "code",
        add_sign: str = "",
    ) -> str:
        if isinstance(num, str):
            num = float(num)
        num = round(num, q_signs_after_comma)
        if float(num) % 1 != 0:
            return "<{format}>{:,.{}f}</{format}>{add_sign}".format(
                float(num), q_signs_after_comma, format=format, add_sign=add_sign
            )
        return "<{format}>{:,}</{format}>{add_sign}".format(
            int(num), format=format, add_sign=add_sign
        )


class ModelTwodd:
    def __init__(self, id_user) -> None:
        self.id_user = id_user

    @staticmethod
    def _create_tag(len_tag: int = 8):
        signs = string.digits + string.ascii_letters
        tag = "".join(random.choices(signs, k=len_tag))
        return tag

    def _wrap(self, text: str):  # sourcery skip: remove-unnecessary-cast
        text = str(text)
        sign_to_replace1 = "꠲"
        sign_to_replace2 = "꠱"
        text = text.replace(":", sign_to_replace1)
        text = text.replace(",", sign_to_replace2)
        return text

    def _unwrap(self, text: str):  # sourcery skip: remove-unnecessary-cast
        text = str(text)
        sign_to_replace1 = "꠲"
        sign_to_replace2 = "꠱"
        text = text.replace(sign_to_replace1, ":")
        text = text.replace(sign_to_replace2, ",")
        return text

    def _unwrap_for_dict(self, d: dict):  # sourcery skip: remove-unnecessary-cast
        sign_to_replace1 = "꠲"
        sign_to_replace2 = "꠱"
        for key in d:
            d[key] = str(d[key]).replace(sign_to_replace1, ":")
            d[key] = str(d[key]).replace(sign_to_replace2, ",")
        return d


weekday_tr = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница",
    "saturday": "Суббота",
    "sunday": "Воскресенье",
}


class Notification(ModelTwodd):
    def __init__(self, id_user) -> None:
        super().__init__(id_user)
        self.__id_notify = None

    def __get(self, name_value):
        self.__check_id_notify
        return self._unwrap(
            flow_db.get_2dd(
                table="users",
                key="notifications",
                where="id",
                meaning=self.id_user,
                where_data="id_notify",
                meaning_data=self.__id_notify,
                get_data=name_value,
            )
        )

    def __del(self, id_notify):
        flow_db.delete_2dd(
            table="users",
            key="notifications",
            where="id",
            meaning=self.id_user,
            unique_value_data=id_notify,
        )

    def __update(self, value, name_value):
        self.__check_id_notify
        flow_db.update_value_2dd(
            table="users",
            key="notifications",
            where="id",
            meaning=self.id_user,
            where_data="id_notify",
            meaning_data=self.__id_notify,
            update_data=name_value,
            value=self._wrap(value),
        )

    def __create(self):
        q_args = len(
            flow_db.get_header_2dd(
                table="users",
                key="notifications",
                where="id",
                meaning=self.id_user,
            )
        )
        tag = self._create_tag()
        flow_db.add_2dd(
            table="users",
            key="notifications",
            where="id",
            meaning=self.id_user,
            throw_data=[tag, *[None for _ in range(q_args - 1)]],
        )
        self.__id_notify = tag

    @property
    def __check_id_notify(self):
        if self.__id_notify is None:
            raise ValueError("id_notify не определен!")

    @property
    def create_notify(self):
        self.__create()

    @property
    def id_notify(self):
        return self.__id_notify

    @id_notify.setter
    def id_notify(self, value):
        self.__id_notify = value

    @property
    def type_notify(self):
        return self.__get("type_notify")

    @type_notify.setter
    def type_notify(self, value):
        self.__update(value=value, name_value="type_notify")

    @property
    def weekday(self):
        return weekday_tr[self.__get("weekday")]

    @weekday.setter
    def weekday(self, value):
        self.__update(value=value, name_value="weekday")

    @property
    def time(self):
        return self.__get("time")

    @time.setter
    def time(self, value):
        self.__update(value=value, name_value="time")

    @property
    def message(self):
        return self.__get("message")

    @message.setter
    def message(self, value):
        self.__update(value=value, name_value="message")

    @property
    def id_preset(self):
        return self.__get("id_preset")

    @id_preset.setter
    def id_preset(self, value):
        self.__update(value=value, name_value="id_preset")

    @property
    def is_active(self):
        return self.__get("is_active")

    @is_active.setter
    def is_active(self, value):
        self.__update(value=value, name_value="is_active")

    def __filter(self, data: list[dict], **kwargs):
        users = None
        for key in kwargs:
            users = [
                self._unwrap_for_dict(notify)
                for notify in data
                if notify[key] == kwargs[key]
            ]
        return users

    def __delitem__(self, key):
        self.__del(id_notify=key)

    def __iter__(self):
        return iter(
            self.__filter(
                flow_db.parse_2dd(
                    table="users",
                    key="notifications",
                    where="id",
                    meaning=self.id_user,
                ),
                is_active=1,
            )
        )

    def __str__(self) -> str:
        return self.message


class Preset(ModelTwodd):
    def __init__(self, id_user) -> None:
        super().__init__(id_user)
        self.__id_preset = None

    def __get(self, name_value):
        self.__check_id_preset
        return self._unwrap(
            flow_db.get_2dd(
                table="users",
                key="presets",
                where="id",
                meaning=self.id_user,
                where_data="id_preset",
                meaning_data=self.__id_preset,
                get_data=name_value,
            )
        )

    def __del(self, id_preset):
        flow_db.delete_2dd(
            table="users",
            key="presets",
            where="id",
            meaning=self.id_user,
            unique_value_data=id_preset,
        )

    def __update(self, value, name_value):
        self.__check_id_preset
        flow_db.update_value_2dd(
            table="users",
            key="presets",
            where="id",
            meaning=self.id_user,
            where_data="id_preset",
            meaning_data=self.__id_preset,
            update_data=name_value,
            value=self._wrap(value),
        )

    def __create(self):
        q_args = len(
            flow_db.get_header_2dd(
                table="users",
                key="presets",
                where="id",
                meaning=self.id_user,
            )
        )
        tag = self._create_tag()
        flow_db.add_2dd(
            table="users",
            key="presets",
            where="id",
            meaning=self.id_user,
            throw_data=[None, tag, None, None],
        )
        self.__id_preset = tag

    @property
    def __check_id_preset(self):
        if self.__id_preset is None:
            raise ValueError("id_preset не определен!")

    @property
    def create_preset(self):
        self.__create()

    @property
    def id_preset(self):
        return self.__id_preset

    @id_preset.setter
    def id_preset(self, value):
        self.__id_preset = value

    @id_preset.deleter
    def id_preset(self):
        self.__del()
        self.__id_preset = None

    @property
    def name_preset(self):
        return self.__get("name_preset")

    @name_preset.setter
    def name_preset(self, value):
        self.__update(value=value, name_value="name_preset")

    @property
    def ids(self) -> list:
        return self.__get("ids").split(",")

    @ids.setter
    def ids(self, value: list):
        if not isinstance(value, list):
            raise ValueError("value для поля ids должен быть типа list")
        str_ids = ",".join(value)
        self.__update(value=str_ids, name_value="ids")

    @property
    def is_active(self):
        return self.__get("is_active")

    @is_active.setter
    def is_active(self, value: int):
        if not isinstance(value, int):
            raise ValueError("value для поля is_active должен быть int")
        self.__update(value=value, name_value="is_active")

    @property
    def current_active_preset(self) -> dict:
        preset = [preset for preset in self.__iter__() if preset["is_active"] == 1]
        return preset[0] if preset else None

    @current_active_preset.setter
    def current_active_preset(self, value: str):
        curr_id_preset = self.__id_preset
        active_preset = self.current_active_preset
        if active_preset:
            self.__id_preset = active_preset["id_preset"]
            self.is_active = 0
        self.__id_preset = value
        self.is_active = 1

        self.__id_preset = curr_id_preset

    def __getitem__(self, item):
        self.__id_preset = item
        return self

    def __delitem__(self, key):
        self.__del(id_preset=key)

    def __iter__(self):
        return iter(
            flow_db.parse_2dd(
                table="users",
                key="presets",
                where="id",
                meaning=self.id_user,
            )
        )


class User(Model):
    def __init__(self, id_user) -> None:
        super().__init__(id_user)
        self.notification = Notification(self.id_user)
        self.preset = Preset(self.id_user)
        self.reasons = Reasons(self.id_user)
        self.__wrap = False

    def __get(self, name_value):
        return flow_db.get_value(key=name_value, where="id", meaning=self.id_user)

    def __update(self, value, name_value):
        return flow_db.update_value(
            key=name_value, where="id", meaning=self.id_user, value=value
        )

    def __switcher_wrap(self, value):
        if self.__wrap:
            self.__wrap = False
            return self._wrap_num(value)
        return value

    @property
    def id(self):
        return self.id_user

    @property
    def date_reg(self):
        return self.__get("date_reg")

    @date_reg.setter
    def date_reg(self, value):
        self.__update(name_value="date_reg", value=value)

    @property
    def fio(self):
        return self.__get("fio")

    @fio.setter
    def fio(self, value):
        self.__update(name_value="fio", value=value)

    @property
    def username(self):
        return self.__get("username")

    @username.setter
    def username(self, value):
        self.__update(name_value="username", value=value)

    @property
    def rule(self):
        return self.__get("rule")

    @rule.setter
    def rule(self, value):
        self.__update(name_value="rule", value=value)

    @property
    def balance_flow(self):
        balance = self.__get("balance_flow")
        return self.__switcher_wrap(balance)

    @balance_flow.setter
    def balance_flow(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("value в balance_flow должен быть int или float")
        self.__update(name_value="balance_flow", value=value)

    @property
    def display(self):
        return self.__get("display")

    @display.setter
    def display(self, value):
        self.__update(name_value="display", value=value)

    @property
    def wrap(self):
        self.__wrap = True
        return self

    @property
    def last_tap_date(self):
        if self.__get("last_tap_date"):
            time = datetime.strptime(self.__get("last_tap_date"), '%d.%m.%Y, %H:%M:%S')
            was_online = datetime.now() - time
            return str(was_online).split('.')[0]
        return None

    @last_tap_date.setter
    def last_tap_date(self, value):
        self.__update(name_value="last_tap_date", value=value)
    
    @property
    def last_tap_button(self):
        if self.__get("last_tap_button"):
            return self.__get("last_tap_button")
        return None

    @last_tap_button.setter
    def last_tap_button(self, value):
        self.__update(name_value="last_tap_button", value=value)

    def __getitem__(self, item):
        if flow_db.user_exists(item):
            return User(item)
        flow_db.add_user(item)
        self.id_user = item
        return self

    def __iter__(self):
        all_users = flow_db.get_all_line_key(key="id")
        return iter(all_users)


class Users:
    def __init__(self, id_user) -> None:
        self.me: User = User(id_user)
        self.id_user = id_user

    def __display_name_sername(self, d: dict):
        d["fio"] = " ".join(d["fio"].split()[::-1])
        return d

    def __display(self, data: list[dict]):
        if User(self.id_user).display == "display_name_sername":
            users = list(map(self.__display_name_sername, data))
        return data

    def __get_ids_active_preset(self) -> list:
        # sourcery skip: assign-if-exp, inline-variable, reintroduce-else
        preset = Preset(self.id_user)
        active_preset = preset.current_active_preset
        if active_preset:
            ids = preset[active_preset["id_preset"]].ids
            return ids
        return None

    def __filter(self, data: list[dict], **kwargs):
        ids = self.__get_ids_active_preset()
        if ids:
            data = [user for user in data if user["id"] in ids]
        users = None
        for key in kwargs:
            users = [user for user in data if user[key] == kwargs[key]]
        return users

    @property
    def to_dict_for_keyboard(self) -> list:
        users = flow_db.get_all_line_key(
            key="rule, fio, id, balance_flow", order="fio", sort_by="ASC"
        )
        users = self.__filter(users, rule="user")
        users = self.__display(users)
        edited_users_list = [
            {
                "fio": user["fio"],
                "balance_flow": user["balance_flow"],
                "select": False,
                "id": user["id"],
                "rule": user["rule"],
            }
            for user in users
        ]
        return edited_users_list

    @property
    def to_dict_for_top(self) -> list:
        users = flow_db.get_all_line_key(
            key="rule, fio, id, balance_flow", order="balance_flow"
        )
        users = self.__filter(users, rule="user")
        users = self.__display(users)
        return users


class Reasons(Model):
    def __init__(self, id_user) -> None:
        super().__init__(id_user)

    def __get_all_reasons(self):
        return flow_db.get_all_reasons(self.id_user)

    def __add_balance_flow(self, value):
        return flow_db.update_value(
            key="balance_flow",
            where="id",
            meaning=self.id_user,
            value=value,
        )

    def __del_reason(self, tag):
        flow_db.delete(
            table="history_reasons",
            where="tag",
            meaning=tag,
        )

    @property
    def data(self):
        return self.__get_all_reasons()

    def __getitem__(self, item):
        return Reason(item)

    def __delitem__(self, key):
        self.__add_balance_flow(-Reason(key).num)
        self.__del_reason(tag=key)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.__get_all_reasons())


class Reason:
    def __init__(self, tag: str = None) -> None:
        self.tag = tag

    @staticmethod
    def _create_tag(len_tag: int = 8):
        signs = string.digits + string.ascii_letters
        tag = "".join(random.choices(signs, k=len_tag))
        return tag

    def __get(self, name_value):
        return flow_db.get_value(
            table="history_reasons", key=name_value, where="tag", meaning=self.tag
        )

    def __update(self, value, name_value):
        return flow_db.update_value(
            table="history_reasons",
            key=name_value,
            where="tag",
            meaning=self.tag,
            value=value,
        )

    def __create(self):
        tag = self._create_tag(10)
        self.tag = tag
        flow_db.add_new_reason(
            tag=tag, id_user="-", reason="-", id_owner_reason="-", date="-", num="-"
        )

    @property
    def create_reason(self):
        self.__create()
        return self

    @property
    def id(self):
        return self.__get("id")

    @id.setter
    def id(self, value):
        self.__update(name_value="id", value=value)

    @property
    def reason(self):
        return self.__get("reason")

    @reason.setter
    def reason(self, value):
        self.__update(name_value="reason", value=value)

    @property
    def owner_reason(self):
        return self.__get("owner_reason")

    @owner_reason.setter
    def owner_reason(self, value):
        self.__update(name_value="owner_reason", value=value)

    @property
    def date(self):
        return self.__get("date")

    @date.setter
    def date(self, value):
        self.__update(name_value="date", value=value)

    @property
    def num(self):
        return self.__get("num")

    @num.setter
    def num(self, value):
        self.__update(name_value="num", value=value)


class Item:
    def __init__(self, id_item) -> None:
        self.id_item = id_item

    def __get(self, name_value):
        return flow_db.get_value(
            table="items", key=name_value, where="id", meaning=self.id_item
        )

    def __update(self, value, name_value):
        return flow_db.update_value(
            table="items",
            key=name_value,
            where="id",
            meaning=self.id_item,
            value=value,
        )

    @property
    def name(self):
        return self.__get("name")

    @name.setter
    def name(self, value):
        self.__update(name_value="name", value=value)

    @property
    def photo(self):
        return self.__get("photo")

    @photo.setter
    def photo(self, value):
        self.__update(name_value="photo", value=value)

    @property
    def description(self):
        return self.__get("description")

    @description.setter
    def description(self, value):
        self.__update(name_value="description", value=value)

    @property
    def price_str(self):
        if self.old_price == 0:
            return f'{self.__get("price")}f'
        price = self.__get("price")
        discount = int((price * 100) / self.old_price) - 100
        return f"<s>{self.old_price}</s> {price}f ({discount}%)"

    @property
    def price(self):
        return self.__get("price")

    @price.setter
    def price(self, value):
        self.old_price = self.__get("price")
        self.__update(name_value="price", value=value)

    @property
    def old_price(self):
        return self.__get("old_price")

    @old_price.setter
    def old_price(self, value):
        self.__update(name_value="old_price", value=value)

    @property
    def quantity(self):
        return self.__get("quantity")

    @quantity.setter
    def quantity(self, value):
        self.__update(name_value="quantity", value=value)

    def generate_qr_code(self):
        """
        Generates a QR code with an embedded link and customization.

        Args:
        link (str): The link to be embedded in the QR code.
        border (int): The width of the border around the QR code.
        box_size (int): The size of each box in the QR code.
        fill_color (str): The color of the boxes in the QR code.
        back_color (str): The background color of the QR code.
        """
        link = f"https://t.me/flowikibot?start={self.id_item}"
        qr = qrcode.QRCode(version=3, box_size=100, border=2)
        qr.add_data(link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#000000", back_color="#ffffff")
        file_name = f"item_{self.id_item}.png"
        if not os.path.exists(file_name):
             img.save(file_name)    
        return file_name


class Items:
    @staticmethod
    def _create_id_item(len_tag: int = 15):
        signs = string.digits + string.ascii_letters
        id_item = "".join(random.choices(signs, k=len_tag))
        return id_item

    def __create(self):
        id_item = Items._create_id_item()
        flow_db.add_new_item(
            id_item=id_item,
            name="-",
            photo="-",
            description="-",
            price=0,
            old_price=0,
            quantity=0,
        )
        return Item(id_item)

    def __del_item(self, id_item):
        flow_db.delete(
            table="items",
            where="id",
            meaning=id_item,
        )

    def __iter__(self):
        return iter(
            flow_db.get_all_line_key(
                key="id, name, photo, description, price, old_price", table="items"
            )
        )

    def __getitem__(self, item):
        if flow_db.item_exists(item):
            return Item(item)
        return self.__create()

    def __delitem__(self, key):
        self.__del_item(id_item=key)


# item = Items()['new_item']
# print(item.id_item)
# u = User('474701274')
# print(list(u.notification))
# u.balance_flow += -1
# u = User("474701274")
# us = Users("474701274")
# pprint(len(us.to_dict_for_keyboard))
# u.preset.current_active_preset = 'cKzU4EIW'
# pprint(len(us.to_dict_for_keyboard))
# pprint(list(us.preset))
# us.preset.current_active_preset = 'QzCoGjl8'
# pprint(us.preset['QzCoGjl8'].is_active)
# # pprint(r.data)
# print(r['z91NcMhClU'].date)
# pprint(r.data)
# # for u in r:
#     print(u)
# print(u.wrap.balance_flow)
# u.notification.id_notify = 'iO4ZDqsx'
# print(u.notification.message)
# for i in u.notification:
#     print(i)
