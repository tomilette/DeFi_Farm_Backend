import imp
from scripts.helpful_scripts import get_account, get_contract
from brownie import PiggyToken, TokenFarm, network, config
from web3 import Web3
import yaml
import json
import os, shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_piggy_token(front_end_update=False):
    account = get_account()
    piggy_token = PiggyToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        piggy_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    tx = piggy_token.transfer(
        token_farm.address, piggy_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    # Start with 5 allowed tokens (piggy_token, weth_token, fau_token/dai, Weenus as UNI, Xeenus as AUD)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    uni_token = get_contract("uni_token")
    aud_token = get_contract("aud_token")
    dict_of_allowed_tokens = {
        piggy_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
        uni_token: get_contract("uni_usd_price_feed"),
        aud_token: get_contract("aud_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    if update_front_end:
        update_front_end()
    return token_farm, piggy_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        set_tx.wait(1)
        return token_farm


def update_front_end():
    # Send the build folder
    copy_folders_to_front_end("./build", "./front_end/src/chain-info")
    # Sending the front end our config in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_piggy_token(front_end_update=True)
