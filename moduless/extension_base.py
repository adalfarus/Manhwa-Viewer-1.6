# Base Class (Needed)
from modules.AutoProviderPlugin import AutoProviderPlugin

# Compiled modules (Can be used without adding a new module yourself)
from urllib.parse import urlencode, urlunparse, quote_plus
from aplustools.web.webtools import Search
from bs4 import BeautifulSoup
import requests
import json
import os
import re


class AutoProviderPluginManhwaClan(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder,
                         cache_folder=cache_folder, provider=provider, specific_provider_website="www.manhwaclan.com",
                         logo_path="./data/ManhwaClanLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "ManhwaClanLogo.png")):
            try:
                # Using base64 is better as it won't matter if the url is ever changed, otherwise pass the url and
                # img_type="url"
                self._download_logo_image('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOsAAABUCAYAAABjlsB1AAAbuUlEQV'
                                          'R4nO2de5xkVXXvv2ufU9XVM93DNPNgmAGUgQwvQcXhMcLwECZiEOFyY/CJjwuicvWD8XpNJCJ8fM'
                                          'eEhChGTAxqiCZqgpKoCDoyQLwqIipBJAPDCAwPZ5hHz6O7q6tq3T/2PnUetau7arpmuufD/n0++3'
                                          'PqnP04u/bZa6+111p7b1FVAgICZj7MdFcgICCgMwRiDQjYRxCINSBgH0HcTeIti6SX797PXbd1nb'
                                          'MGMncIBoegNm6fyR4ad0wEtSq6+SlQBWPsuwRAwZTcuxUQkELAtZnLK3E5U7gvfZI2gqjkyiVfno'
                                          'gtVjLFmPR3MQ5Rz7N89XL5is8Bkr/sS2O0maYlj6/8LEq51vDWM4dY7Xs0U/92/6GT/5qtfxYKUs'
                                          'ZSSDHa9x4FiYAok76ZZoL2h3y7CZQvf6S1PnRJrGnpPcFJwC/pllgbCpFAuQKNRi/rExAwo9EdsZ'
                                          'qoV+/9PeAy4KKuczZqMHsQ+mZBrdqr+gQEzHh0yVl7JmquAl6JUOsqlyrEMVIZAA1cNeC5henirC'
                                          '8CLYPMAYY7ztWoQ18/lMpQ747OAwL2dXRJrD3jrAe760rg294UqjZkISDlSq/nzgEB+wSmSwye76'
                                          '6XIvLtpiYVR6AKxCVHlI5gkyRxOSiWAp6TmC4xOFHYn49wEPBEk4tGJWveKPVlTCIZaD3MVwOek5'
                                          'guMThLgTeBnGFtTQYplyFy1dIGTeNUwmSDK3PAcxRdUZ+I6VXYlPl9uoh5v5gIKZVABer1zHzVUa'
                                          'gGSg14bqM7VmlMj0L0a0xEGuQTwCWBIAMC2qNLYo16FMz3C8QLJvo74JpArAEBfnRHrGJ6Fb6LMR'
                                          'tbOK6Yq0BWk5p2AgICHLoj1sj0KtQQ8ykkIhcshz0TkfuBF7evSIvX+VHA0G63woRIPMYDAqYXXX'
                                          'LWqHfBRF/EGG0zp90PMT9C5JAWETqKffPgMiLX9pDzpyEqWbtuvRGINmBaMV2mG4CNwC9oz0ErwF'
                                          '0gz7drjLJosbP+EuEUkBuwCwR6AwWiGB3b5Vb79KzkgICuMX2c1YZfTRJ/CGJuSteQJtwublVaSf'
                                          'RviHkbElV6Vr9SCerjsGs4LNMPmHZMk+mmGTZ0kOZ1GHkZkdAMRnzp7rRXeYeN70Eo9aHbN8NY3c'
                                          '61AwKmEV0Sa89DtaN0wpfdNQ2t6eru+rqe1C0S0BqMBK4aMDMw3cQ6v8N0SxBeO0mahe56HIY5U6'
                                          'qXKPSVYWQb7BrvdmYfELBH0FU33APbHD2vi7QfAb46Qfzp7lrGruoZ3t1KgQFRdMsm56MRtMAB04'
                                          '8utcE9fruyvIvUSxFeCvwok9/COvn/YSbt6FQqRaWCbt2MDo9a0g8ImAHojlj7Jkguxjrg12p0yI'
                                          'leiHBgV++HtyAZYk2gXI00d0t8Cnimy3JTmMiKwZs22vvAVANmCLoiVt2ytX1krYYMzoY5AzBWhV'
                                          'p9MieCV3fzbodzm7/Sok9A+VAmzTeB+m6UbdFfRp/cgG4btZbegIAZgu6IdeOWdjFQHUM3b0YWzk'
                                          'fmzbW20PHaRAT7v7p5t8OBwLHA/e5+EFidIdwG8NFstTqGKvRXYHgr+sSm3H62AQEzAd2JwaUJkk'
                                          'cCY6PoI0+hw9sxSw9GYmM9f4oQXgss6q6qTZxKQqzKLQgDmbhvAhtcXGL26QxRjFZHafz2CXvv29'
                                          'w5IGAa0TujhCpEEVQUnt0Bi3bCfoNQHfel/vPdfw/HAwnBn1GI+5a7WkLtg+YOE5NAZpXQRzehw3'
                                          'VkoLM8AQF7E723IEYG1TqMjyMlg7buGHoFykG7Xb4w2/263hP3c8BtuEbHhEqSyZA//iAgYAZhz5'
                                          'j7Fdi5y2pVTe75AuCvpqhhHQPeQOuSuFHgSSD1cOpqzppkDAiYmdhjvjlaq6EC9tAfRwTKN3tQ9E'
                                          'rgbM/zrS7sPs31dlVRQEBPsUeIVQxotYY0amhskIaiyvucU8NUcVib57FYITZRae3vwsOTlpiMJ7'
                                          'VaEIEDZiz2DCuJgJEqVGtIFIFwqAh/XjzdsMdhCGF+5hTFcREuEIOZdI15LEi9RuPZ4T12cmRAwF'
                                          'Sx54h1TNGRUaRkQLhpDywCKIaIiEOJmvfbMZyL4VWT5ZVKRGPnCGyvBvtqwIzFnuIj/4MaQ4hCpG'
                                          'dj9KUYZS+EE61SqxkGEf3opPn6InT7LnR0D7ZIQMAU0eOuqQcjslbHOI0FlV1m4SA6Pv7Xe4GrJg'
                                          '4QFxaercZwNIbDJ8qnNNBdY71tioCAHqNHxKqgnIREazHRwUTmPdHSBWNUohVo45i9RqyGlRgOyo'
                                          'jCv3RE/LWmN1MxxMa6RW4fDetWA2Y0esVZjyeKfkxc7tNxOdssnEN04GwYq/6xRLJHNh2cIFwj0v'
                                          'y93l1fLMIV3q2WSoKMj6OjVSQQa8AMRnfdM/ImH0Qba0BAWIvo3WbxIPSZAar1C6ZhDvhW4MPAeu'
                                          'A32BU4EfBXwB0Iv8jZYSOc2cZrsxHgNGA/oJp5FgF3kl/g/gJgqSfdeuC/2tT1GKwpqoodOBvAbb'
                                          'Ru37gYOBq7DijxCYuAcZc+wQnAAZn//Dvgp1gHkhXuHVmfshKwxdXxhe5ZvRC/E1gNzAZOBma592'
                                          'bT7ADuwBq+XuTaYR1298oy1i6e3RvybvfeIk4CFrg6xli7+d2edEUcC5yHNdM9CSwHPg/sAt4NfA'
                                          '94CPst55J+I3DyFfAo7b9TFiux/SGpY9LGRRyN3VxBSL9nyaX/Seb+DOx3Tdr9v2ljbuxupwgfsS'
                                          'pfBLXO9HW9SebEyIIKOl5/BYZ4mpyCvo5dOvcswsPAEa6u30c4FGF7M6UqzIqhFKE76/Ys9pRUYu'
                                          'xhz7NpgXwC+FPUeWkpVwP/01OXrwEXtannd2k9feAUkOKa3bdgd8rwVIO3Itzo7j4DnJiJvRfbcV'
                                          '9Cu0Or4XHgky5vO4gr4/veWKWKoR9LrD/EEsROYADroV1898mkHTbBfODHntLnAZtzCzPScbUCfB'
                                          'bbPgDXAfdhB+aPY///KcCFWGL9lqubD7cA57eJS7AUO0gXUcF61mXxaeBlbco5DDuYDZAfbAE+Bf'
                                          'xfX6bu+F5UKoT4SKL4wuZ9Pb7dDFUwsw3UGqvazhP3fFiO4WrHNX+c2WRtHsKa5j83QKOBzCoRv2'
                                          'QxADri0lqMYzvpak9rvLHQc7Z70nwbuLx5lxiFU+xozSKnImKPu0yPvLweeK+nfIC/QYndoXuvJu'
                                          'VEd5N2vjuA/+3JWwMuRPg88EFP/FasxABwD+231bkQaKAsIyEGYbYox6Jsx7ZhglOBn+R2+bCo4t'
                                          'kQGisRpGnT9ANYwkwI9QfAnwJfwv7vCpZQAcbd+07ADk5FXA+8LfckcVnNo50Wcjnuk2UGkjcDf9'
                                          '8m/Zfc4YhbEFYAm9zzz9FuUPZWZyJEcTF8nDjGhR0al+6VoRLECsKJe1Gx5NMMfwjheAxFbfSLMX'
                                          'wvu0ui7qpinjeXeOWBtvvmFh/IQyBvoRVLSDqSbxmgxRpQu5GTgJhklYALwg9acggvbdatUXNpZS'
                                          'twLf6PP4DwKddJHgPeB4DyTtQtFxRqWFGwiG0oPwPGEW73xD8CPOAcTUYQz4hviWeTe/+Zhdhz3P'
                                          'OfYwnxBuA/m/mSZYg2DOMfFDPEqtkzer8LHJlJ9zmUERd3C1bkTRCprefDFEVMO97+K8ozzbIbrm'
                                          '7JxCSt4wYsty7CeuapPevb4XGES7EcvYhTEV7ues2PgS+65+9ggr3Ddp+zxqWDiEoXZJ49RFyuUo'
                                          'kQ0UGJWLaXFUu+cLcYzhHD5sLz3xfh2qwHFNtHiY9aQPyCIXSMNLERsETwm9YGkYtsZl0CjHhabH'
                                          '/AitrJi5rnzrIC5VFPHtc5HQtJtGVICbgU2ObJcwXCQa7k5JvutB1Xk6J8W+hEwBz3+wBPfNFF5A'
                                          'mKnMm6ar7BvWNFIf2Z7vkRrl430sDOzpIByVZ6MVY0vstTB1tmwlFt+vOwHDqLdLcsm/YuaA5AWY'
                                          '7d73lH2jauEcWQ5ZJgRddTaRVbQTg5J9kljMHiYs/7AL6QkbF2kEhmPtnCoUtijdJgovfkuKzET0'
                                          'klRiqA8nwM/dPKWW3ox/DxNnV5D4bTMpwYUGTB7NRXOD8/+nJLewing56GFa8m2ffJfRo7QvcDfw'
                                          'e6g2TxQYqFIMfk5XrAEtMK4AMtRds6/kPuziqCpgrJlWjh437LXdqUWG2ele7uLPcsnafmdRmHYu'
                                          'ebvsHrRETLiGbzvMuTzud79ll33d8T1x5+PcuxwMeABz1x7XzeV2LF+8974pYgzalNH6mo3hbdEW'
                                          'vcDIaIS4igGQxbqAAVUFg0Awi1SLS+51/N3ddqSCVCKgK1RraTzkP5L89HPAKVG+lk61PJEd7JWE'
                                          '3wGqzGtAjb6VXtRMhmexq7E8bj+AlmlcAhwFp338k+VDGpZvTpDtIDHtHdzmuX06qIG8DuCHJOpl'
                                          '75gdCG07CKsTtpnccPkJ/zlrHt50fyzewA/AOspvaJ9n+nDVq/9RnYuamP+y8Cjsr9p3SY+wrwBa'
                                          'xmuohkE4an8XP8HLoi1ox98gKJmJOzV8aMiYCgYHT2XnIvnGpYjNF3Jvc6XkPmlZH9ymh+g4sLEQ'
                                          'ZQbi40ST9WQzhCYabrR7N3vt49eAhrNinCN1LXgIXA4cBr2rzgJlIO08l2bzuBuSgno477+ZAnAN'
                                          '/cdgBlCf558SqscLe6WVZepAWrjPkFwm/xc9eseL0Uu/dW+7qm5W7HmoN+0NUBgCajLErLex1WUb'
                                          'cev5LK982eBI4Cfgu808M5Dda0tI4Ojj3rkrOqDZFe3PydhjmUNJmYy5Q1umaK+TsPH2lyVlVksI'
                                          'QM9RX1fvOxo/m/+htGb2MS4pB8b/kj4Huu197vWZd3SvFBBodgT+D7oSduJVax8h6XbjI8gXAk8P'
                                          '+wIl4neBq/NHA4tjMXcRZ2EPkmkJ9ipFgGfMM1wz2eMrKcdGjSGtbZvaWOSipl5TW7Faz9t9M6Jk'
                                          'gGzvnAlxCPvkG5DtvbPgzN7XS96HLOCkT0E3FOTgSOgBJzVUGrgsTUpii23orwJxg27AUReYjkaA'
                                          '4BiQSzf1/xnz8JvAaRh2jtBhtdmHgP5JRY9wMZBG5087A1uXS29GUIS6xY1dLrKi7Rm9u86Vrs/N'
                                          'pnsyxiMcp/Ywn86okSFqrh464vxy9KXwTchXJrjkOnSDTI/+iu+fawsIOXzT+BCoZUvG5avSgODB'
                                          'MjYRJ5cfY8F/sNd70jl8fW6xQrWXqRbGP0jjZvfR/WZDPhELM7YvCZEtMnMRTCQSLY/hexfQoa3M'
                                          '0ivAL4pBhet5e0xlc0la4NReb22Sl/2i3GgYWo3kerUfw77hPNoR2S+aodrS9wveBfXL57QTzKKT'
                                          'm5zaevZ8w013niF2OVUJ1sdD4IbEa4C+E7HaRP4HOOOBvbn4oKmNTemXCuvOLuYnf3mLu/jdZOux'
                                          'hhmfs98dw6ITCTKaUTLpvlqi59xm76JuxcOtFLtGqErbjr06hDOkX6Kn4vqVXAq5hE79GlGAzEnJ'
                                          'lRNGXDYcQMuA6+PqfC7i6UiThWrDh9yl5SQJ2I4XkYoF63onDF2NPO8+1Ux3pHZfEf7tpmUFVSk0'
                                          '0D0ItB1mAdCbagbMT/kV+aaKg93DV52//BzjuLeC+dbfVaIzV5TCwZJFWw485d+E1VvsEM8vbQtD'
                                          'xb5vlYZ4D3Y10QH8Tflsmc8DEmG4gSF1KLBcCsjgg2zXMzwr9k7ldhPbw+htXe+8TgtI6t79LC4O'
                                          'RDW2eIBN0Ra8QghhPadPg+DEdrDTA8huHp3ZxDDmD4M1fm2/bSvBWSReoo0m+QSpTVp7qRUQD550'
                                          'yL1EBvdb87nSW9DLjZpX8Uq2Ra60nXzhxQy4hoNfyeSTARp58KbAceodVndx3W7/XXnlyp2Jwnw0'
                                          'HsHPRmbGs/AvyKZOO7PFa4Flb8Yrg2y0/fUcEqg1496cdJ8tjx+QLsHByUA7ED2s3YfvAw1snjd5'
                                          '5SivPW8cIVhPtoHfA7Qrdi8DESc7RHBEZiMGXOVBVUaRDx093mdMLXXaN/uqP0qflo94NwJga03k'
                                          'Dm9WHmV6xzhIXjIgrCs6QnAqwBdrj5qI/DNdX1bmh9vpMBbwe9GTgea2j3jbbHg4k9Q0CtOZe1He'
                                          'yL+L1kihs2++rXIOWQvnhr1snO4VIUCSbxZy7OlZ8B7slpgdPpRXKEyu3AX2DNP6eTPVUhRXbe6l'
                                          'OGbQVSMdaKsNdhJzRZTuhzGczSwbvdNRFX3+ze+1PgKlfHM/BPQU4ptFViFit+i8s8eSc9TK1LMV'
                                          'gPI9YFHk2wDX16KWNqq1jmtgJBrMZwfweEsxHDN9zvv6WTA5eFmxCuxaBTINjjEJBKhG4do/HsCF'
                                          'ImmbgkneqP3fXLAKgTga2YeqBHeNu/OdQrgDpneZnXzGfzrPO0dhnhFU0/YXSVe/5KRMqIpEoU4U'
                                          '3e75XUx3acAU+KMkLkOpePE6ea14QAUhTnrQmnvRfYnHl+R05ZkxCTMgvcGUXSouH1SRrHICx26R'
                                          '+klaBPKrT/u7D+vtcBv85E7e8pe8zlfT0pEa51ed7n3ln0kPJ9sxMQ54xiB4tL3fPLc/N0YQt+X+'
                                          'wJ0S1nXeJdE5raWg8DVumwIIavZRQ4NyCcheE4MTw4ibLno5nfI2K4bpL0P8HwRoT3iuHqKSiZni'
                                          '+G+TIY03h4G/XHa4kP0NexHxGEv8SurvmCbRH9tuOq6/AftHUFyIdIPFTSg7XuJBVf+4CftWnyW2'
                                          'h1czsCyx0OyHC6n5DOnROUXZ1BORu/lnUAyxEvBv7NE78UK5IO0BwzmnH3FdLe7d5XL8Td1axHQq'
                                          'iWM+0kNS9thqad93n4FThgj0Y53A0af4ZdWZPgA1gCPQ0rrv4N1mR0hSO6EsqDWE+kFLY+FeDfXf'
                                          'oEV7rYZCAZI1nRpByJf1FD2f2vCnYwuco9fwOJT7Q2h++PkF8muIxJ0N161ph5kyWRiE83RjjSjL'
                                          'JR+rlFa7yKBo9JxSBlg+6opZ2oFVuxjZzFNViO1mo0bigyOz5ASgYdHgdlQVdq+jwi4EBUN8lgCY'
                                          'lIfFh/gRUza1izyZMgW7AfIOEA38ASY1HcmQU8gP3onweexY65c4ENNDVIfAW/GDSE7SRbsMu+hj'
                                          'PPxwvmhTeRinCQn1NtwrrebSyUL678DdglXZsL8QZL0LWcJjfFH2I7/6j7nwmuJOW0X/P8r81Yp/'
                                          '5Es7uQdNXSWJu6gFUWZdeifgA7mL4WqwsYwhL7euBqEuKzdVbsErmv02r+uRfrffUr0m/Yh51TJy'
                                          'tiFpFOa6oT1HG+uz4AfML9n4jk+2anA1ZxlZiFNnjKykHUp2lsgx1vXHY98M7J0mmVK8xcvS5ayN'
                                          'E6zgOUpK5bqkfo1rFHoqPmfE531C+j4TFKKReAO68GsvGXk11v6aosQ4bGozv/oL5ux3fjkxZeRV'
                                          '2v2S1jeIpTMfKfUokY/ed11NdVMUOuIk2Pf3Gs2FXOGE+87964LC5v8ttIh/mL964dMprPpkdjtl'
                                          '2jpLEyzzPFFJ9RLCMrShvscoIiTOYdGVlNinXJsgbPu1rq37zX1v9lJkqffyZZ+dGbRievTwft1L'
                                          '49lWzdW3YkKci35Xc9gg/disFjbUTgNRKxM7k3Ff5aR2RpYxe/pqy3ypxSVH9g0/zRf3p6qL6et8'
                                          'uAfMwuo8sEo1/B6Ldy7oCpv9f1iP4I49JGiuyn63WrWTL278N3jt+z7TCkMUJJ8mXmy6eZv30Yp1'
                                          'FHZhtKy+chrfO0gIBpQ3cKpogtBc+lBhHnAWdgWE5M1XkzIRF36BYiarySUu0Wrfc9zaz5D4z/3F'
                                          'xe3yBXErMS4X5Xzj0Ir59EiXQORn5HH8gsrqw/IYeOfU9LWl6wzRxy2CU6zGek3Gif385nzsXw6A'
                                          'TveYZI0O1Vot8bxCwxdl1MQMAMQJfEqk8RWc7mQo1Y/0P6FUr6G4xuJXYcrKwHI/xMd0hdn6md36'
                                          'jOf0n0goUHmkX6GR3mb1Huln6Oo6Hn07po2SIrSkSyXavjxzGqh9cfMzfW15rrzDxdX3phOZID+k'
                                          '7XnTIiRh9uozz6qUR8RiK+I4aPt0nzrBg2iAFqitkvJj4uWds6tUYOCOgFuhODYx6SEtukZOcuUq'
                                          'IsMR+hxFIp0UfEeRLxfSlZuVwqvIgGTzU2maVmrlkdLak9FR1cJ1rSeLuZw+1mniIxt1Dz2vhaa1'
                                          'rVZxrP8IiOyfnxssa746MaRAfViA+rrpAKZR2TDxbsrU9j+DSGs4ioELME4/yAW8O9GOfTHIGO1o'
                                          'mOnIMMgo5ObSIcENALdLm7Ifch/JL8lhlXolyJ4QExvIAGqxBOR3grcC7KIpnFI/ERtau0yiozXz'
                                          '9s9tcnpcy1RK4Go3SwQAhwe3PIbP2cmae30s+bxHAWVu39eq1yI3UuwbAW5TsotyGMIZSwniz7Y9'
                                          'oekPGt7I2O1IgWV4iPHWD87h3IYnZvJUdAQI/QrelmB3Zp1mme2GMQPgRcwzhrUNZgGMSwHFhBxM'
                                          'EibJCIC+1Zb6TLkDoVMxORuAHUZD1Gr6Gi10iJEiUWsVXQ7ZzdPBA5na/eRXsna7BGmptyTxS0Vq'
                                          'f88gNoPDpCY7iODHQyogQE7Bl0qw1GIr7azt1QDFdLzCKpuJIbbAd+iOFjNHgHdbY2ibQXaJBscD'
                                          'ZOjcdzi4WTBQaG12A4aRLvpU9gGM49i0B31DCLK8QnD1lFU5i7BkwjutUGQ8RDRPzM2+mtze8GYp'
                                          'BZ2KW3dfaO+cMRktKcTyN2EfwNXttYEgy/Q7jKGxcLurNGtGw2Zr5Bx4IcHDB96I5Y050iPtDWPz'
                                          'jWVxHp0cSKma1IP/SUm/qQiMYKpkIq3AvvF8OcCd0M4RwRGu3OfWVnnWhBGXNAH4wEo2vA9GF3xG'
                                          'Ak4naJuaetOBzxl+I4rQwoMujWNo3T3Ry144oBY67QEgnHjDF8cBLx948w3DdhGhSZHWEW9RX3ZQ'
                                          'oI2KvoVhucxWsQ/H5Rdje7Q3GbX1mRWGFHxk2u1c+0cyR7z7pVJzqG3Wg7X783MNF2nMqFqNw86X'
                                          'ClQNlgBqPgzRQwrehSDM6FdcRc3mbXCIi5rPlbrHgaLVC7HqEq1l06cedLCC8b6q1Ba6RrTPsVqW'
                                          'TmkK0eT5e04ZY7EZaD26lQJwkAdUXHtfcSQUBAF+juYKpW0v4shuPwL6Z9JfAnLWW41Sw6aglWyp'
                                          'o50iWTLlHyJARjwAyAzFOY3cD0q11GWsc35MxDPTstCKMop6Le3fkCAmY0uhOD/Xg7kQ5ht9fM4h'
                                          'js0qfW7S8ScVWBCph+zTscKHbhd7r+0S7UnhfZVR91RWvW976NM8XxaIH8hfUo56p6tx0JCJjx6A'
                                          'WxgnAREVspnsQ1lSMciku0EtNM9vTT9mJppRD39yhX4N+6JCBgn0BviBVAuEwMD2F33JuF3RD7tz'
                                          '0rP31PJ1iNPfGs5rZeWRtcBQP2dXS1+DwgIGD60J02OCAgYNoQiDUgYB9BINaAgH0EgVgDAvYRBG'
                                          'INCNhHEIg1IGAfQSDWgIB9BIFYAwL2Efx/h079yrlaUBoAAAAASUVORK5CYII=',
                                          "ManhwaClanLogo", img_format='png', img_type="base64")
            except Exception as e:
                print(f"An error occurred {e}")
                return

    def _direct_provider(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://manhwaclan.com',
            'Referer': 'https://manhwaclan.com/',
        }

        # Define the URL for the request
        url = 'https://manhwaclan.com/wp-admin/admin-ajax.php'

        # Define the data for the first POST request
        data = {
            'action': 'wp-manga-search-manga',
            'title': self.title
        }

        # Send the first POST request
        response = requests.post(url, headers=headers, data=data)

        # Check for a successful response (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()
            url = self._get_url(response_data["data"][0]["url"] + f"chapter-{self.chapter_str}/",
                                f'chapter {self.chapter} {self.title.title()}')
            if url:
                print("Found URL:" + url)  # Concatenate (add-->+) string, to avoid breaking timestamps
                return url
        else:
            print(f'Error: {response.status_code}')
        return None

    def _indirect_provider(self):
        url = self._get_url(
            f'https://{self.specific_provider_website}/manga/{"-".join(self.url_title.lower().split())}/chapter-{self.chapter_str}/',
            f'chapter {self.chapter} {self.title.title()}')
        if url:
            print("Found URL:" + url)  # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

    def get_search_results(self, text):
        if text is None:
            return True
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://manhwaclan.com',
            'Referer': 'https://manhwaclan.com/',
        }

        # Define the URL for the request
        url = 'https://manhwaclan.com/wp-admin/admin-ajax.php'

        # Define the data for the first POST request
        data = {
            'action': 'wp-manga-search-manga',
            'title': text
        }

        # Send the first POST request
        response = requests.post(url, headers=headers, data=data)

        # Check for a successful response (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            response_data = json.loads(response.text)
            titles = [data.get("title") for data in response_data["data"]]
            # urls = [self._get_url(data["url"] + f"chapter-{self.chapter_str}/", f'chapter {self.chapter} {self.title.title()}') for data in response_data["data"]]
            return ([title, "data\\reload_icon.png"] for title in titles)  # list(zip(titles, url_results))
        else:
            print(f'Error: {response.status_code}')
        return None
