import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

interface PaymentDetails {
  job_id: string;
  payment_status: string;
  amount_usdc?: number;
  asset_id?: number;
  network: string;
  receiver_wallet?: string;
  transaction_id?: string;
  payer_wallet?: string;
}

const API_BASE_URL = 'http://127.0.0.1:8000';

const PaymentPage = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [payment, setPayment] =
    useState<PaymentDetails | null>(null);

  const [transactionId, setTransactionId] =
    useState('');

  const [payerWallet, setPayerWallet] =
    useState('');

  const [error, setError] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [verifying, setVerifying] =
    useState(false);

  useEffect(() => {
    if (!jobId) return;

    const loadPayment = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/jobs/${jobId}/payment`,
        );

        if (!response.ok) {
          const payload = await response.json();

          throw new Error(
            payload.detail ||
              'Unable to load payment details.',
          );
        }

        const data: PaymentDetails =
          await response.json();

        setPayment(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load payment details.',
        );
      } finally {
        setLoading(false);
      }
    };

    loadPayment();
  }, [jobId]);

  const handleVerifyPayment = async () => {
    if (!jobId) return;

    if (!transactionId.trim()) {
      setError('Please enter the Algorand transaction ID.');
      return;
    }

    if (!payerWallet.trim()) {
      setError('Please enter the payer wallet address.');
      return;
    }

    setVerifying(true);
    setError(null);

    try {
      // ----------------------------------------------------
      // STEP 1: Verify transaction on Algorand
      // ----------------------------------------------------

      const verifyResponse = await fetch(
        `${API_BASE_URL}/api/jobs/${jobId}/payment/verify`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            transaction_id: transactionId.trim(),
            payer_wallet: payerWallet.trim(),
          }),
        },
      );

      const verifyData =
        await verifyResponse.json();

      if (!verifyResponse.ok) {
        throw new Error(
          verifyData.detail ||
            'Payment verification failed.',
        );
      }

      setPayment(verifyData);

      // ----------------------------------------------------
      // STEP 2: Payment verified → process job
      // ----------------------------------------------------

      const processResponse = await fetch(
        `${API_BASE_URL}/api/jobs/${jobId}/process`,
        {
          method: 'POST',
        },
      );

      const processData =
        await processResponse.json();

      if (!processResponse.ok) {
        throw new Error(
          processData.detail ||
            'Payment verified, but processing could not start.',
        );
      }

      // ----------------------------------------------------
      // STEP 3: Continue to processing page
      // ----------------------------------------------------

      navigate(`/processing/${jobId}`);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Payment verification failed.',
      );
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div className="py-10">
        <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">
          <p className="text-slate-300">
            Loading payment details...
          </p>
        </div>
      </div>
    );
  }

  if (error && !payment) {
    return (
      <div className="py-10">
        <div className="rounded-3xl border border-rose-900 bg-rose-950/60 p-8">
          <h2 className="text-2xl font-semibold text-rose-200">
            Payment Error
          </h2>

          <p className="mt-3 text-rose-300">
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!payment) {
    return null;
  }

  return (
    <div className="space-y-8 py-10">

      {/* Header */}
      <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8 shadow-xl shadow-slate-900/20">

        <p className="text-sm uppercase tracking-[0.24em] text-sky-400">
          Algorand TestNet Payment
        </p>

        <h2 className="mt-3 text-3xl font-semibold text-white">
          Complete Payment
        </h2>

        <p className="mt-2 max-w-2xl text-slate-400">
          Send the required ALGO amount to the CodeVerse
          receiver wallet. After payment, enter your
          transaction ID and wallet address to verify the
          transaction on-chain.
        </p>

        {/* Payment information */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2">

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <p className="text-sm text-slate-400">
              Amount due
            </p>

            <p className="mt-2 text-3xl font-semibold text-white">
              {payment.amount_usdc?.toFixed(3)} ALGO
            </p>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <p className="text-sm text-slate-400">
              Network
            </p>

            <p className="mt-2 text-lg font-semibold uppercase text-white">
              {payment.network}
            </p>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:col-span-2">
            <p className="text-sm text-slate-400">
              Receiver wallet
            </p>

            <p className="mt-2 break-all font-mono text-sm text-white">
              {payment.receiver_wallet}
            </p>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <p className="text-sm text-slate-400">
              Asset
            </p>

            <p className="mt-2 text-lg font-semibold text-white">
              {payment.asset_id === 0
                ? 'Native ALGO'
                : `Asset ${payment.asset_id}`}
            </p>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <p className="text-sm text-slate-400">
              Payment status
            </p>

            <p className="mt-2 text-lg font-semibold capitalize text-white">
              {payment.payment_status}
            </p>
          </div>

        </div>
      </div>

      {/* Verification */}
      <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">

        <p className="text-sm uppercase tracking-[0.24em] text-sky-400">
          Blockchain Verification
        </p>

        <h3 className="mt-2 text-2xl font-semibold text-white">
          Verify Your Transaction
        </h3>

        <p className="mt-2 text-slate-400">
          Enter the transaction ID generated after your
          Algorand payment and the wallet that sent the
          payment.
        </p>

        <div className="mt-6 space-y-5">

          {/* Transaction ID */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Transaction ID
            </label>

            <input
              type="text"
              value={transactionId}
              onChange={(event) =>
                setTransactionId(event.target.value)
              }
              placeholder="Enter Algorand transaction ID"
              className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4 font-mono text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-sky-500"
            />
          </div>

          {/* Payer wallet */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Payer Wallet Address
            </label>

            <input
              type="text"
              value={payerWallet}
              onChange={(event) =>
                setPayerWallet(event.target.value)
              }
              placeholder="Enter the wallet that sent ALGO"
              className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4 font-mono text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-sky-500"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="rounded-2xl border border-rose-900 bg-rose-950/70 px-4 py-4 text-sm text-rose-300">
              {error}
            </div>
          )}

          {/* Verify button */}
          <button
            type="button"
            onClick={handleVerifyPayment}
            disabled={
              verifying ||
              !transactionId.trim() ||
              !payerWallet.trim()
            }
            className="inline-flex w-full items-center justify-center rounded-3xl bg-emerald-500 px-6 py-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {verifying
              ? 'Verifying on Algorand...'
              : 'Verify Payment & Continue'}
          </button>

        </div>
      </div>

    </div>
  );
};

export default PaymentPage;