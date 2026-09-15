import json
import statistics
import time
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen2.5:1.5b-instruct",
    "phi3:3.8b",
]

SYSTEM_PROMPT = """
You are the customer support assistant for GadgetMart, a fictional UK electronics store.

GadgetMart sells five products:

1. Wireless Bluetooth Headphones Pro
Price: £79.99
Specifications:
- 40-hour battery life
- Active noise cancellation (ANC)
- USB-C charging
- Foldable design with carrying case
- Bluetooth 5.2

Unknown:
- Available colours
- Extended warranty options beyond the standard 1-year warranty
- Water resistance rating

2. Ergonomic Laptop Stand Aluminium
Price: £34.99
Specifications:
- Adjustable height with 6 positions
- Fits laptops from 11" to 17"
- Aluminium construction
- Non-slip silicone pads
- Ventilated design

Unknown:
- Maximum weight capacity
- Compatibility with specific laptop brands/models

3. Mechanical Keyboard RGB 87-Key
Price: £89.99
Specifications:
- 87-key TKL layout
- Cherry MX Brown switches
- RGB backlighting
- Detachable USB-C cable
- Compatible with Windows and Mac

Unknown:
- Keycap material
- Required software or drivers

4. Full HD Webcam 1080p
Price: £49.99
Specifications:
- 1080p at 30fps
- Built-in dual microphones
- USB-A plug-and-play
- Adjustable clip mount
- Works with Zoom, Microsoft Teams and Skype

Unknown:
- Low-light performance
- Field of view

5. Portable Power Bank 20000mAh
Price: £29.99
Specifications:
- 20000mAh
- Dual USB-A outputs
- One USB-C output
- 18W fast charging
- LED battery indicator
- Can charge most smartphones 4-5 times

Unknown:
- Exact recharge time
- Airline carry-on compliance

Shipping:
- UK mainland only
- Free standard shipping for orders £50 or more
- £4.99 standard shipping for orders under £50
- No express or next-day delivery
- Standard delivery is 3-5 business days after dispatch
- Orders before 2 PM Monday-Friday are typically dispatched the same day
- Weekend orders are dispatched Monday
- Tracking link is sent by email after dispatch
- Tracking may take up to 24 hours to appear
- Carrier is fictional Royal Mail Tracked 48

Tracking:
- Processing = order received and being prepared
- Dispatched = handed to carrier
- In Transit = travelling to local delivery office
- Out for Delivery = with postal carrier for delivery today
- Delivered = successfully delivered
- Attempted Delivery = delivery attempted but nobody was available

The assistant CANNOT:
- Look up orders
- Access tracking systems
- Change delivery addresses
- Upgrade shipping
- Process returns
- Approve refunds
- Generate return labels
- Access customer accounts

Return policy:
- Change-of-mind: notify within 14 days of delivery
- Item must be unused and in original unopened packaging
- Customer pays return postage
- Refund within 14 days of GadgetMart receiving acceptable return
- Faulty/damaged: report within 30 days
- No sealed/unused requirement for genuinely faulty items
- GadgetMart covers return postage
- Full refund or replacement offered
- All five products are eligible
- Customers should email support@gadgetmart-demo.co.uk

For missing product information, explicitly say that the information is not included in the product details provided.

Never invent product specifications.

Never claim that you checked an order, tracking system, inventory, or customer account.

Stay within GadgetMart's domain.

Use concise, helpful British English.
"""


def load_prompts():
    path = Path(__file__).parent / "benchmark_prompts.json"

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def benchmark_model(model, prompt):
    payload = {
        "model": model,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0
        },
    }

    try:
        start_time = time.perf_counter()
        first_token_time = None
        response_text = ""
        token_count = 0

        with requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=(30, 60),
        ) as response:

            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                data = json.loads(line.decode("utf-8"))

                if first_token_time is None and data.get("response"):
                    first_token_time = time.perf_counter()

                response_text += data.get("response", "")

                # Ollama provides eval_count at the final response.
                if data.get("done"):
                    token_count = data.get("eval_count", 0)

        end_time = time.perf_counter()

        total_time = end_time - start_time

        if first_token_time is None:
            ttft = total_time
        else:
            ttft = first_token_time - start_time

        generation_time = end_time - first_token_time if first_token_time else total_time

        tokens_per_second = (
            token_count / generation_time
            if generation_time > 0
            else 0
        )

        return {
            "response": response_text.strip(),
            "ttft_seconds": round(ttft, 4),
            "total_seconds": round(total_time, 4),
            "tokens": token_count,
            "tokens_per_second": round(tokens_per_second, 2),
        }

    except requests.exceptions.Timeout:
        print("  [TIMEOUT: Request exceeded 60 seconds of inactivity]")
        return {
            "response": "[TIMEOUT]",
            "ttft_seconds": None,
            "total_seconds": None,
            "tokens": 0,
            "tokens_per_second": 0,
        }

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR: {type(e).__name__}: {str(e)}]")
        return {
            "response": f"[ERROR: {type(e).__name__}]",
            "ttft_seconds": None,
            "total_seconds": None,
            "tokens": 0,
            "tokens_per_second": 0,
        }


def main():
    prompts = load_prompts()
    results = []

    print("=" * 70)
    print("GadgetMart Local LLM Benchmark")
    print("=" * 70)

    for model in MODELS:
        print(f"\nMODEL: {model}")
        print("-" * 70)

        for item in prompts:
            prompt_id = item["id"]
            prompt = item["prompt"]

            print(f"\n[{prompt_id}] {prompt}")
            print("Running benchmark... please wait.")

            result = benchmark_model(model, prompt)

            result_record = {
                "model": model,
                "prompt_id": prompt_id,
                "prompt": prompt,
                **result,
            }

            results.append(result_record)

            # Save after every prompt to preserve results if interrupted
            output_path = Path(__file__).parent / "benchmark_results.json"
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=2, ensure_ascii=False)

            print(f"TTFT: {result['ttft_seconds']} seconds")
            print(f"Tokens: {result['tokens']}")
            print(f"Tokens/sec: {result['tokens_per_second']}")
            print(f"Response: {result['response']}")

    output_path = Path(__file__).parent / "benchmark_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"Results saved to: {output_path}")
    print("=" * 70)

    print_summary(results)


def print_summary(results):
    print("\nSUMMARY")
    print("-" * 70)

    models = sorted(set(result["model"] for result in results))

    for model in models:
        model_results = [
            result for result in results
            if result["model"] == model
        ]

        # Filter out None values for TTFT calculation
        ttfts = [
            result["ttft_seconds"]
            for result in model_results
            if result["ttft_seconds"] is not None
        ]

        # Filter out zero/failed results for tokens/sec calculation
        speeds = [
            result["tokens_per_second"]
            for result in model_results
            if result["tokens_per_second"] > 0
        ]

        print(f"\n{model}")
        
        if ttfts:
            print(
                f"Average TTFT: "
                f"{statistics.mean(ttfts):.3f} seconds"
            )
        else:
            print("Average TTFT: N/A (all prompts timed out)")
        
        if speeds:
            print(
                f"Average tokens/sec: "
                f"{statistics.mean(speeds):.2f}"
            )
        else:
            print("Average tokens/sec: N/A (all prompts timed out)")
        
        # Show timeout/error count if any
        failed_count = len([r for r in model_results if r["ttft_seconds"] is None])
        if failed_count > 0:
            print(f"Failed/Timed out: {failed_count}/{len(model_results)} prompts")


if __name__ == "__main__":
    main()