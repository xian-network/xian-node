import os
import sys
import unittest

from xian.processor import TxProcessor
from contracting.client import ContractingClient
from fixtures.mock_constants import MockConstants
from utils import setup_fixtures, teardown_fixtures

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Change the current working directory
os.chdir(script_dir)


def submission_kwargs_for_file(f):
    # Get the file name only by splitting off directories
    split = f.split("/")
    split = split[-1]

    # Now split off the .s
    split = split.split(".")
    contract_name = split[0]

    with open(f) as file:
        contract_code = file.read()

    return {
        "name": f"con_{contract_name}",
        "code": contract_code,
    }


TEST_SUBMISSION_KWARGS = {
    "sender": "stu",
    "contract_name": "submission",
    "function_name": "submit_contract",
}

node_1 = "7fa496ca2438e487cc45a8a27fd95b2efe373223f7b72868fbab205d686be48e"
node_2 = "dff5d54d9c3cdb04d279c3c0a123d6a73a94e0725d7eac955fdf87298dbe45a6"
node_3 = "6d2476cd66fa277b6077c76cdcd92733040dada2e12a28c3ebb08af44e12be76"
node_4 = "b4d1967e6264bbcd61fd487caf3cafaffdc34be31d0994bf02afdcc2056c053c"
node_5 = "db21a73137672f075f9a8ee142a1aa4839a5deb28ef03a10f3e7e16c87db8f24"


from datetime import datetime, timedelta
import time

def create_block_meta(dt: datetime = datetime.now()):
    # Get the current time in nanoseconds
    nanos = int(time.mktime(dt.timetuple()) * 1e9 + dt.microsecond * 1e3)
    # Mock b_meta dictionary with current nanoseconds
    return {
        "nanos": nanos,                # Current nanoseconds timestamp
        "height": 123456,              # Example block number
        "chain_id": "test-chain",      # Example chain ID
        "hash": "abc123def456"         # Example block hash
    }


class MyTestCase(unittest.TestCase):

    def setUp(self):
        setup_fixtures()
        self.c = ContractingClient(storage_home=MockConstants.STORAGE_HOME)
        self.tx_processor = TxProcessor(client=self.c)
        # Hard load the submission contract
        self.d = self.c.raw_driver
        self.d.flush_full()

        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct absolute paths for the contract files
        submission_contract_path = os.path.abspath(
            os.path.join(
                script_dir,
                "../../xian-contracting/src/contracting/contracts/submission.s.py",
            )
        )
        currency_contract_path = os.path.abspath(
            os.path.join(
                script_dir,
                "../../src/xian/tools/genesis/contracts/currency.s.py",
            )
        )
        dao_contract_path = os.path.abspath(
            os.path.join(
                script_dir, "../../src/xian/tools/genesis/contracts/dao.s.py"
            )
        )
        rewards_contract_path = os.path.abspath(
            os.path.join(
                script_dir,
                "../../src/xian/tools/genesis/contracts/rewards.s.py",
            )
        )
        stamp_cost_contract_path = os.path.abspath(
            os.path.join(
                script_dir,
                "../../src/xian/tools/genesis/contracts/stamp_cost.s.py",
            )
        )
        members_contract_path = os.path.abspath(
            os.path.join(
                script_dir,
                "../../src/xian/tools/genesis/contracts/members.s.py",
            )
        )
        foundation_contract_path = os.path.abspath(
            os.path.join(
                script_dir,
                "../../src/xian/tools/genesis/contracts/foundation.s.py",
            )
        )

        with open(submission_contract_path) as f:
            contract = f.read()
        self.d.set_contract(name="submission", code=contract)

        with open(currency_contract_path) as f:
            contract = f.read()
        self.c.submit(
            contract,
            name="currency",
            constructor_args={
                "vk": "7fa496ca2438e487cc45a8a27fd95b2efe373223f7b72868fbab205d686be48e"
            },
        )
        self.d.set(
            key="currency.balances:7fa496ca2438e487cc45a8a27fd95b2efe373223f7b72868fbab205d686be48e",
            value=100000,
        )
        self.d.set(
            key="currency.balances:dff5d54d9c3cdb04d279c3c0a123d6a73a94e0725d7eac955fdf87298dbe45a6",
            value=100000,
        )
        self.d.set(
            key="currency.balances:6d2476cd66fa277b6077c76cdcd92733040dada2e12a28c3ebb08af44e12be76",
            value=100000,
        )
        self.d.set(
            key="currency.balances:b4d1967e6264bbcd61fd487caf3cafaffdc34be31d0994bf02afdcc2056c053c",
            value=100000,
        )
        self.d.set(
            key="currency.balances:db21a73137672f075f9a8ee142a1aa4839a5deb28ef03a10f3e7e16c87db8f24",
            value=100000,
        )
        self.d.set(key="currency.balances:new_node", value=1000000)

        with open(dao_contract_path) as f:
            contract = f.read()
        self.c.submit(contract, name="dao", owner="masternodes")

        with open(rewards_contract_path) as f:
            contract = f.read()
        self.c.submit(contract, name="rewards", owner="masternodes")
        self.d.set(key="rewards.S:value", value=[0.88, 0.01, 0.01, 0.1])

        with open(stamp_cost_contract_path) as f:
            contract = f.read()
        self.c.submit(contract, name="stamp_cost", owner="masternodes")
        self.d.set(key="stamp_cost.S:value", value=20)

        with open(members_contract_path) as f:
            contract = f.read()
        self.c.submit(
            contract,
            name="masternodes",
            constructor_args={
                "genesis_registration_fee": 100000,
                "genesis_nodes": [
                   node_1,
                   node_2,
                   node_3,
                   node_4,
                   node_5,
                ],
            },
        )

        with open(foundation_contract_path) as f:
            contract = f.read()
        self.c.submit(
            contract,
            name="foundation",
            constructor_args={
                "vk": node_1
            },
        )

        self.currency = self.c.get_contract("currency")
        self.dao = self.c.get_contract("dao")
        self.rewards = self.c.get_contract("rewards")
        self.stamp_cost = self.c.get_contract("stamp_cost")
        self.masternodes = self.c.get_contract("masternodes")

    def tearDown(self):
        teardown_fixtures()
        self.d.flush_full()

    def register(self):
        approve_currency = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": "new_node",
                    "contract": "currency",
                    "function": "approve",
                    "kwargs": {"amount": 100000, "to": "masternodes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": {"nanos": 0, "hash": "0x0", "height": 0, "chain_id": "test-chain"},
            }
        )
        register_node = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": "new_node",
                    "contract": "masternodes",
                    "function": "register",
                    "kwargs": {},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": {"nanos": 0, "hash": "0x0", "height": 0, "chain_id": "test-chain"},
            }
        )

    def unregister(self):
        unregister_node = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": "new_node",
                    "contract": "masternodes",
                    "function": "unregister",
                    "kwargs": {},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": {"nanos": 0, "hash": "0x0", "height": 0, "chain_id": "test-chain"},
            }
        )

    def vote_in(self):
        block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {"type_of_vote": "add_member", "arg": "new_node"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )

    def vote_out(self, block_meta=None):
        if block_meta is None:
            block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {
                        "type_of_vote": "remove_member",
                        "arg": "new_node",
                    },
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        # breakpoint()
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 2, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 2, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 2, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote5 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_5,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 2, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        return [vote, vote2, vote3, vote4, vote5]

    def vote_in_and_unregister(self):
        block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {"type_of_vote": "add_member", "arg": "new_node"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        self.unregister()
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        return [vote, vote2, vote3, vote4]

    def vote_stamp_cost(self):
        block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {"type_of_vote": "stamp_cost_change", "arg": 30},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4= self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )

    def vote_reward_change(self):
        block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {
                        "type_of_vote": "reward_change",
                        "arg": [0.78, 0.11, 0.01, 0.1],
                    },
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )

    def vote_dao_payout(self):
        block_meta = create_block_meta(datetime.now())
        vote1 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {
                        "type_of_vote": "dao_payout",
                        "arg": {"amount": 100000, "to": "new_node", "contract_name": "currency"},
                    },
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )

    def vote_reg_fee_change(self):
        block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {
                        "type_of_vote": "change_registration_fee",
                        "arg": 200000,
                    },
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        

    def vote_types_change(self):
        block_meta = create_block_meta(datetime.now())
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {
                        "type_of_vote": "change_types",
                        "arg": [
                            "new_type1",
                            "new_type2",
                            "new_type3",
                            "new_type4",
                        ],
                    },
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote2 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote3 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_3,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        vote4 = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_4,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )

    def announce_leave(self, block_meta=None):
        if block_meta is None:
            block_meta = create_block_meta(datetime.now())
        announce = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": "new_node",
                    "contract": "masternodes",
                    "function": "announce_leave",
                    "kwargs": {},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )

    def leave(self, block_meta=None):
        if block_meta is None:
            block_meta = create_block_meta(datetime.now() + timedelta(days=8))
        leave = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": "new_node",
                    "contract": "masternodes",
                    "function": "leave",
                    "kwargs": {},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": block_meta,
            }
        )
        return leave

    def test_register(self):
        self.register()
        self.assertEqual(
            self.masternodes.pending_registrations["new_node"], True
        )
        self.assertEqual(self.currency.balances["new_node"], 900000)

    def test_unregister(self):
        self.register()
        self.unregister()
        self.assertEqual(
            self.masternodes.pending_registrations["new_node"], False
        )
        self.assertEqual(self.currency.balances["new_node"], 1000000)

    def test_register_propose_unregister_and_validate(self):
        self.register()
        self.assertEqual(
            self.masternodes.pending_registrations["new_node"], True
        )
        self.assertEqual(self.currency.balances["new_node"], 900000)

        res = self.vote_in_and_unregister()
        
        assert res[3].get('tx_result').get('result') == "AssertionError('Member must have pending registration')"

        self.assertEqual(
            self.masternodes.pending_registrations["new_node"], False
        )
        self.assertEqual(self.currency.balances["new_node"], 1000000)

        nodes = self.masternodes.nodes.get()
        self.assertNotIn(
            "new_node", nodes,
            "The node should not be in the list of validators after unregistering."
        )

    def test_vote_in_node(self):
        self.register()
        self.vote_in()
        self.assertEqual(self.masternodes.votes[1]["yes"], 4)
        self.assertEqual(self.masternodes.votes[1]["no"], 0)
        self.assertEqual(self.masternodes.votes[1]["finalized"], True)
        nodes = self.masternodes.nodes.get()
        self.assertIn("new_node", nodes)

    def test_vote_out_node(self):
        self.register()
        self.vote_in()
        self.vote_out()
        self.assertEqual(self.masternodes.votes[2]["yes"], 5)
        self.assertEqual(self.masternodes.votes[2]["no"], 0)
        self.assertEqual(self.masternodes.votes[2]["finalized"], True)
        nodes = self.masternodes.nodes.get()
        self.assertNotIn("new_node", nodes)

    def test_announce_leave(self):
        self.register()
        self.vote_in()
        self.announce_leave()

    def test_leave(self):
        self.register()
        self.vote_in()
        self.announce_leave()
        self.leave()
        self.assertEqual(self.masternodes.pending_leave["new_node"], False)
        
    def test_leave_not_pending(self):
        self.register()
        leave_res = self.leave().get('tx_result').get('result')
        self.assertEqual(leave_res, "AssertionError('Not pending leave')")
        
    def test_expired_proposal(self):
        proposal_block_meta = create_block_meta(datetime.now())
        expired_block_meta = create_block_meta(datetime.now() + timedelta(days=8))
        
        # Propose
        
        vote = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_1,
                    "contract": "masternodes",
                    "function": "propose_vote",
                    "kwargs": {
                        "type_of_vote": "remove_member",
                        "arg": "new_node",
                    },
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": proposal_block_meta,
            }
        )
        
        expired_vote_res = self.tx_processor.process_tx(
            tx={
                "payload": {
                    "sender": node_2,
                    "contract": "masternodes",
                    "function": "vote",
                    "kwargs": {"proposal_id": 1, "vote": "yes"},
                    "stamps_supplied": 1000,
                },
                "metadata": {"signature": "abc"},
                "b_meta": expired_block_meta,
            }
        ).get('tx_result').get('result')
        self.assertEqual(expired_vote_res, "AssertionError('Proposal expired')")

    def test_force_leave(self):
        self.register()
        self.vote_in()
        self.vote_out()
        self.leave()
        self.assertEqual(self.masternodes.pending_leave["new_node"], False)

    def test_leave_payback(self):
        self.register()
        self.vote_in()
        self.announce_leave()
        self.leave()
        self.unregister()
        self.assertEqual(self.currency.balances["new_node"], 1000000)

    def test_force_leave_payback(self):
        self.register()
        self.vote_in()
        self.vote_out()
        self.leave()
        self.unregister()
        self.assertEqual(self.currency.balances["new_node"], 1000000)
        
    def test_leave_before_pending_period_passed(self):
        self.register()
        self.vote_in()
        self.announce_leave()
        leave_res = self.leave(create_block_meta(datetime.now())).get('tx_result').get('result')
        self.assertEqual(leave_res, "AssertionError('Leave announcement period not over')")

    def test_stamp_rate_vote(self):
        self.assertEqual(self.stamp_cost.S["value"], 20)
        self.vote_stamp_cost()
        self.assertEqual(self.masternodes.votes[1]["yes"], 4)
        self.assertEqual(self.masternodes.votes[1]["no"], 0)
        self.assertEqual(self.masternodes.votes[1]["finalized"], True)
        self.assertEqual(self.stamp_cost.S["value"], 30)

    def test_reward_change_vote(self):
        self.assertEqual(self.rewards.S["value"], [0.88, 0.01, 0.01, 0.1])
        self.vote_reward_change()
        self.assertEqual(self.masternodes.votes[1]["yes"], 4)
        self.assertEqual(self.masternodes.votes[1]["no"], 0)
        self.assertEqual(self.masternodes.votes[1]["finalized"], True)
        self.assertEqual(self.rewards.S["value"], [0.78, 0.11, 0.01, 0.1])

    def test_dao_payout(self):
        self.assertEqual(self.currency.balances["new_node"], 1000000)
        self.vote_dao_payout()
        self.assertEqual(self.masternodes.votes[1]["yes"], 4)
        self.assertEqual(self.masternodes.votes[1]["no"], 0)
        self.assertEqual(self.masternodes.votes[1]["finalized"], True)
        self.assertEqual(self.currency.balances["new_node"], 1100000)

    def test_reg_fee_change(self):
        self.assertEqual(self.masternodes.registration_fee.get(), 100000)
        self.vote_reg_fee_change()
        self.assertEqual(self.masternodes.votes[1]["yes"], 4)
        self.assertEqual(self.masternodes.votes[1]["no"], 0)
        self.assertEqual(self.masternodes.votes[1]["finalized"], True)
        self.assertEqual(self.masternodes.registration_fee.get(), 200000)

    def test_types_change(self):
        self.assertEqual(
            self.masternodes.types.get(),
            [
            "add_member", 
            "remove_member", 
            "change_registration_fee", 
            "reward_change", 
            "dao_payout", 
            "stamp_cost_change", 
            "change_types", 
            "create_stream", 
            "change_close_time", 
            "finalize_stream", 
            "close_balance_finalize",
            "topic_vote"
            ],
        )
        self.vote_types_change()
        self.assertEqual(self.masternodes.votes[1]["yes"], 4)
        self.assertEqual(self.masternodes.votes[1]["no"], 0)
        self.assertEqual(self.masternodes.votes[1]["finalized"], True)
        self.assertEqual(
            self.masternodes.types.get(),
            ["new_type1", "new_type2", "new_type3", "new_type4"],
        )


if __name__ == "__main__":
    unittest.main()
