import warnings
from typing import Optional
from ._types import UserChannel, UserClientType, GameType
from ._exceptions import ComboTokenInvalidError


class User:
    """
    用户类。
    """

    def __init__(
            self,
            combo_token: str,
            sys_version: str,
            device_id: str,
            device_name: str,
            device_model: str,
            client_type: UserClientType,
            *,
            game_type: Optional[GameType] = None,
            channel: Optional[UserChannel] = UserChannel.Official
    ):
        """
        创建一个用户。

        Args:
            combo_token (str): 对应 headers 中的 x-rpc-combo_token。
            sys_version (str): 对应 headers 中的 x-rpc-sys_version。
            device_id (str): 对应 headers 中的 x-rpc-device_id。
            device_name (str): 对应 headers 中的 x-rpc-device_name。
            device_model (str): 对应 headers 中的 x-rpc-device_model。
            client_type (UserClientType): 用户的客户端种类。
            game_type (Optional[GameType]): 游戏类型，若为空则将会从 combo_token 中自动识别。
            channel (Optional[UserChannel]): 用户的游戏渠道。

        Raises:
            ComboTokenInvalidError: 当 combo_token 不合法。
            NotImplementedError: 当使用了不支持的平台 / 游戏类型。
            SyntaxWarning: 当自动识别的游戏类型与用户手动指定的类型不符。
        """
        self._combo_token = combo_token
        self._sys_version = sys_version
        self._device_id = device_id
        self._device_name = device_name
        self._device_model = device_model
        self._client_type = client_type
        self._game_type = game_type
        self._channel = channel

        # Validation check.

        ct_map = {}

        for seg in self._combo_token.split(';'):
            key = seg.split('=')[0]
            value = seg.split('=')[1]
            ct_map[key] = value

        missing_keys = [key for key in ['ai', 'ci', 'oi', 'ct', 'si', 'bi'] if key not in ct_map.keys()]

        if missing_keys:
            raise ComboTokenInvalidError(f"Combo token missing keys: {', '.join(missing_keys)}")

        # Automatic detection of the game type.

        game_type_map = {
            "hk4e_cn": GameType.GenshinImpact,
            "hkrpg_cn": GameType.StarRail,
            "nap_cn": GameType.ZZZ
        }

        if ct_map['bi'] not in game_type_map.keys():
            raise ComboTokenInvalidError(f"{ct_map['bi']} was not supported.")

        detected_game_type = game_type_map[ct_map['bi']]

        if self._game_type is None:
            self._game_type = detected_game_type
        else:
            if self._game_type != detected_game_type:
                warnings.warn(
                    "The program detected a difference between the GameType you entered and the GameType it detected. "
                    "This time, it will use your input as the standard. So the data may be incorrect.”"
                    "Please pay attention to the GameType.",
                    SyntaxWarning
                )

        # PCWeb for ZZZ

        if self._game_type == GameType.ZZZ and self._client_type == UserClientType.PCWeb:
            raise NotImplementedError("ZZZ's PC Web is not supported. Use Android.")

    def get_user_headers(self) -> dict:
        """
        获取该用户的 headers。

        Returns:
            字典格式的该用户的 header。
        """
        return {
            "x-rpc-combo_token": self._combo_token,
            "x-rpc-sys_version": self._sys_version,
            "x-rpc-device_id": self._device_id,
            "x-rpc-device_name": self._device_name,
            "x-rpc-device_model": self._device_model,
            # Client type in headers must be string.
            "x-rpc-client_type": str(self._client_type.value),
            "x-rpc-channel": self._client_type
        }

    @property
    def combo_token(self) -> str:
        return self._combo_token

    @property
    def sys_version(self) -> str:
        return self._sys_version

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_name(self) -> str:
        return self._device_name

    @property
    def device_model(self) -> str:
        return self._device_model

    @property
    def client_type(self) -> UserClientType:
        return self._client_type

    @property
    def game_type(self) -> GameType:
        return self._game_type

    @property
    def channel(self) -> UserChannel:
        return self._channel
