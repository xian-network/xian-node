import json
import asyncio

from cometbft.abci.v1beta2.types_pb2 import Event, EventAttribute
from cometbft.abci.v1beta3.types_pb2 import (
    ResponseFinalizeBlock,
    ExecTxResult
)
from xian.utils.hash import (
    hash_list,
    hash_from_rewards,
    hash_from_validator_updates
)
from xian.utils.block import (
    get_nanotime_from_block_time,
    convert_cometbft_time_to_datetime
)
from xian.utils.tx import (
    verify,
    unpack_transaction
)
from xian.utils.encoding import (
    decode_transaction_bytes,
    convert_binary_to_hex,
    stringify_decimals,
    hash_bytes
)
from loguru import logger


async def finalize_block(self, req) -> ResponseFinalizeBlock:
    nanos = get_nanotime_from_block_time(req.time)
    hash = convert_binary_to_hex(req.hash)
    block_datetime = convert_cometbft_time_to_datetime(nanos)
    height = req.height
    tx_results = []
    reward_writes = []

    self.current_block_meta = {
        "nanos": nanos,
        "height": height,
        "hash": hash,
        "chain_id": self.chain_id
    }

    for tx_bytes in req.txs:
        tx = decode_transaction_bytes(tx_bytes)
        sender, signature, payload = unpack_transaction(tx)

        if not verify(sender, payload, signature):
            # Not really needed, because check_tx should catch this first, but just in case
            # Skip this transaction
            continue

        # Attach metadata to the transaction
        tx["b_meta"] = self.current_block_meta

        try:
            result = self.tx_processor.process_tx(
                tx,
                enabled_fees=self.enable_tx_fee,
                rewards_handler=self.rewards_handler
            )
        except Exception as e:
            logger.error(f"Error processing tx: {e}")
            # Skip this transaction
            continue

        self.nonce_storage.set_nonce_by_tx(tx)
        tx_hash = result["tx_result"]["hash"]
        self.fingerprint_hashes.append(tx_hash)
        parsed_tx_result = json.dumps(stringify_decimals(result["tx_result"]))
        logger.debug(f"Parsed tx result: {parsed_tx_result}")

        tx_events = []

        # Only trigger state change events if tx was successful
        if result["tx_result"]["status"] == 0:
            # Need to replace chars since they are reserved
            translation_table = str.maketrans({'.': '_', ':': '__'})

            state_changes = []

            for state in result['tx_result']['state']:
                state_key = state['key'].translate(translation_table)
                state_value = str(state['value'])

                state_changes.append(
                    EventAttribute(key=state_key, value=state_value)
                )

            if state_changes:
                tx_events.append(Event(
                    type='StateChange',
                    attributes=state_changes
                ))

        tx_results.append(
            ExecTxResult(
                code=result["tx_result"]["status"],
                data=parsed_tx_result.encode(),
                gas_used=0,
                events=tx_events
            )
        )

        if self.block_service_mode:
            cometbft_hash = hash_bytes(tx_bytes).upper()
            result["tx_result"]["hash"] = cometbft_hash
            asyncio.create_task(self.bds.insert_full_data(tx | result, block_datetime))

    if self.block_service_mode:
        asyncio.create_task(self.bds.db.commit_batch_to_disk())

    if self.static_rewards:
        try:
            reward_writes.append(self.rewards_handler.distribute_static_rewards(
                master_reward=self.static_rewards_amount_validators,
                foundation_reward=self.static_rewards_amount_foundation,
            ))
        except Exception as e:
            logger.error(f"STATIC REWARD ERROR: {e} for block")

    reward_hash = hash_from_rewards(reward_writes)
    validator_updates = self.validator_handler.build_validator_updates()
    validator_updates_hash = hash_from_validator_updates(validator_updates)
    self.fingerprint_hashes.append(validator_updates_hash)
    self.fingerprint_hashes.append(reward_hash)
    self.fingerprint_hash = hash_list(self.fingerprint_hashes)

    return ResponseFinalizeBlock(
        validator_updates=validator_updates,
        tx_results=tx_results,
        app_hash=self.fingerprint_hash
    )
