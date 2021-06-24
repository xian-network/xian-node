"""
Base Application

Note:
Tendermint creates 4 connections to the application below through the 
server.  Each connection belongs to certain functions.  Tendermint automatically
handles synchronization of these calls - they are linearlized by tendermint.

The connections:
Query connection:
- info()
- query()

Mempool connection:
- check_tx()

Consensus connection:
- init_chain()
- begin_block()
- deliver_tx()
- end_block()
- commit()

State Sync connection:
- list_snapshots()
- offer_snapshots()
- load_snapshot_chunks()
- apply_snapshot_chunks()
"""

# from .utils import str_to_bytes
from tendermint.abci.types_pb2 import (
    RequestApplySnapshotChunk,
    RequestInitChain,
    RequestListSnapshots,
    RequestLoadSnapshotChunk,
    RequestOfferSnapshot,
    ResponseApplySnapshotChunk,
    ResponseInitChain,
    RequestInfo,
    ResponseInfo,
    ResponseDeliverTx,
    ResponseCheckTx,
    RequestQuery,
    ResponseListSnapshots,
    ResponseLoadSnapshotChunk,
    ResponseOfferSnapshot,
    ResponseQuery,
    RequestBeginBlock,
    ResponseBeginBlock,
    RequestEndBlock,
    ResponseEndBlock,
    ResponseCommit,
)

CodeTypeOk = 0


class BaseApplication:
    """
    Base ABCI Application. Extend this and override what's needed for your app
    """

    def init_chain(self, req: RequestInitChain) -> ResponseInitChain:
        """
        Called only once - usually at genesis or when blockheight == 0.
        See info()
        """
        return ResponseInitChain()

    def info(self, req: RequestInfo) -> ResponseInfo:
        """
        Called by ABCI when the app first starts. A stateful application
        should alway return the last blockhash and blockheight to prevent Tendermint
        from replaying the transaction log from the beginning.  This values are used
        to help Tendermint determine how to synch the node.
        If blockheight == 0, Tendermint will call init_chain()
        """
        r = ResponseInfo()
        r.last_block_height = 0
        r.last_block_app_hash = b""
        return r

    def deliver_tx(self, tx: bytes) -> ResponseDeliverTx:
        """
        Process the tx and apply state changes.
        This is called via the consensus connection.
        A non-zero response code implies an error and will reject the tx
        """
        return ResponseDeliverTx(code=CodeTypeOk)

    def check_tx(self, tx: bytes) -> ResponseCheckTx:
        """
        Use to validate incoming transactions.  If the returned resp.code is 0 (OK),
        the tx will be added to Tendermint's mempool for consideration in a block.
        A non-zero response code implies an error and will reject the tx
        """
        return ResponseCheckTx(code=CodeTypeOk)

    def query(self, req: RequestQuery) -> ResponseQuery:
        """
        This is commonly used to query the state of the application.
        A non-zero 'code' in the response is used to indicate and error.
        """
        return ResponseQuery(code=CodeTypeOk)

    def begin_block(self, req: RequestBeginBlock) -> ResponseBeginBlock:
        """
        Called during the consensus process.  The overall flow is:
        begin_block()
         for each tx:
           deliver_tx(tx)
        end_block()
        commit()
        """
        return ResponseBeginBlock()

    def end_block(self, req: RequestEndBlock) -> ResponseEndBlock:
        """Called at the end of processing. If this is a stateful application
        you can use the height from here to record the last_block_height"""
        return ResponseEndBlock()

    def commit(self) -> ResponseCommit:
        """
        Called after the end of a block.  Normally this should return the results
        of the computation, such as the root hash of a merkletree.  The returned
        data is used as part of the consensus process.
        """
        return ResponseCommit()

    def list_snapshots(self, req: RequestListSnapshots) -> ResponseListSnapshots:
        """
        State sync: return state snapshots
        """
        return ResponseListSnapshots()

    def offer_snapshot(self, req: RequestOfferSnapshot) -> ResponseOfferSnapshot:
        """
        State sync: Offer a snapshot to the application
        """
        return ResponseOfferSnapshot()

    def load_snapshot_chunk(
        self, req: RequestLoadSnapshotChunk
    ) -> ResponseLoadSnapshotChunk:
        """
        State sync: Load a snapshot
        """
        return ResponseLoadSnapshotChunk()

    def apply_snapshot_chunk(
        self, req: RequestApplySnapshotChunk
    ) -> ResponseApplySnapshotChunk:
        """
        State sync: Apply a snapshot to state
        """
        return ResponseApplySnapshotChunk()
