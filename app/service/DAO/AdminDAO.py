from service.BaseApi.StrapiApi import StrapiApi


class AdminDAO:

    async def get_admins():
        url = "/admin"
        admins = await StrapiApi.get(url)
        return admins["admins_id"]["admins"]

    async def get_bot_settings(setting):
        url = "/bot-settings"
        res = await StrapiApi.get(url)

        base_settings = {
            "bonuses_from_post": 15,
        }
        if setting in res["settings"]:
            return res["settings"][setting]

        return base_settings[setting]

    async def get_tech_url():
        url = "/admin"
        admins = await StrapiApi.get(url)
        return admins["admins_id"]["techUrl"]