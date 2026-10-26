import base64
import streamlit as st 
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

st.title("Cosmetic Cycle")
st.write("Give expired cosmetic waste a second life by DIY them into new painting products!")

st.subheader("Tell us about your cosmetic product")
product_name = st.text_input("What is the product name?")

product_type = st.selectbox(
    "What type of cosmetic is it?",
    [   
        "Lipstick", 
        "Lip Gloss",
        "Highlighter",
        "Eyeshadow", 
        "Foundation", 
        "Blush", 
        "Mascara",
        "Other"],
        index=None
        )

ingredients = ""
uploaded_image = None

input_method = st.radio(
    "How would you like to provide the ingredients?",
    ["Paste ingredients", "Upload a photo"],
    index=None
)

if input_method == "Paste ingredients":
    ingredients = st.text_area(
        "Paste the ingredients list here. Write 'Unknown' if the ingredients are not available.",
    )

elif input_method == "Upload a photo":
    uploaded_image = st.file_uploader(
        "Upload a photo of the ingredients label",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded ingredients label")

product_condition = st.multiselect(
    "Have you noticed any unusual changes in the product? Please select 'No noticeable changes' or other conditions, but not both.",
    [
        "No noticeable changes",
        "Visible mold",
        "Unusual smell",
        "Change in color",
        "Change in texture",
        "Separation of ingredients",
        "Other unusual changes",
    ],
    placeholder="Select all that apply"
)
if len(product_condition)>1:
    cleaned_conditions=[]

    for condition in product_condition:
        if condition != "No noticeable changes":
            cleaned_conditions.append(condition)
    product_condition = cleaned_conditions
    
if st.button("Continue"):
    if not product_name.strip():
        st.error("Please enter the product name.")

    elif product_type is None:
        st.error("Please select the cosmetic type.")

    elif input_method is None:
        st.error("Please choose how to provide the ingredients.")

    elif input_method == "Paste ingredients" and not ingredients.strip():
        st.error("Please paste the ingredients list.")

    elif input_method == "Upload a photo" and uploaded_image is None:
        st.error("Please upload a photo of the ingredients label.")

    elif not product_condition:
        st.error("Please select the product condition.")

    else:
        st.success("Information submitted successfully! Please wait for the response.")

        prompt = f"""
        The user wants to reuse a cosmetic product as an art material, usually for drawing or pigment-related art.

        Product name: {product_name}
        Cosmetic type: {product_type}
        Ingredients: {ingredients if input_method == "Paste ingredients" else "Ingredients provided as an image"}
        Product condition: {", ".join(product_condition)}

        PROJECT BACKGROUND AND EXPERIMENTAL FINDINGS
        Our research team has conducted practical experiments on repurposing expired cosmetics as drawing materials. The following findings are based on our team's own experiments:
        Lipstick, lip gloss, eyeshadow, and green color-correcting primer:
        Lip gloss could be applied directly to paper and left to dry. In our experiments, the resulting color did not come off after wiping.
        Lipstick was difficult to dry and tended to smudge when applied to paper. Our team used a fixative spray designed for oil pastels to reduce smudging.
        Green color-correcting primer performed well as a coloring material in our experiments. It dried quickly and showed good color retention.
        Eyeshadow-based watercolor:
        Our team crushed and ground eyeshadow, then mixed it with makeup remover and a small amount of water to create a watercolor-like material that could be applied with a paintbrush.
        Glitter particles could come loose from the eyeshadow pigment. Our team used a fixative spray to reduce this problem, and comparative experiments showed improvement.
        Fixative spray:
        Our experiments identified poor drying, smudging, and pigment transfer as challenges when using cosmetics as drawing materials.
        A fixative spray designed for oil pastels formed a film that helped reduce pigment wear and transfer onto hands.

        YOUR TASK
        Analyze the user's cosmetic product and provide a personalized response focused exclusively on drawing materials, pigments, and artistic coloring experiments. Do not suggest unrelated DIY products or general repurposing ideas.
        Your response MUST contain exactly two main sections, in the following order:
        
        SECTION 1: Suggestions
        Provide one clear, practical drawing or pigment-making method tailored to the user's cosmetic product.
        Present the method as numbered steps using the exact format "Step 1:", "Step 2:", "Step 3:", and so on.
        Make each step short, specific, and easy for a beginner to follow.
        Include the materials needed and explain how to use them at each relevant step.
        Briefly describe the expected artistic effect or result.
        If ingredients are unknown, base the method on cosmetic type and general knowledge without assuming specific ingredients.
        Include relevant safety precautions where necessary but avoid repetitive warnings or lengthy explanations.
        Do not present untested methods as experimentally verified results.
        If the product shows visible mold, an unusual smell, or other abnormal changes, do not provide reuse instructions; advise the user not to reuse it.
        Keep this section under 200 words.

        SECTION 2: Research Team's Experimental Findings
        Present only the relevant findings from the research team's experiments listed in the project background above.
        Select findings that match the user's cosmetic type or are directly relevant to the proposed artistic use.
        Accurately preserve the original experimental observations. Do not invent additional findings, alter the results, or present AI-generated ideas as research team findings.
        
        If no directly relevant experiment is available for the user's product, explicitly state: “Our research team has not conducted a directly relevant experiment on this specific cosmetic type.”
        This section is for reference. It must remain separate from Section 1.

        SAFETY REQUIREMENTS
        Successful coloring performance does not establish that an expired cosmetic is safe to handle or reuse.
        If the product has visible mold, an unusual smell, or other abnormal changes, advise against reusing it as an art material.
        Do not recommend reusing a product that shows signs of deterioration simply because a potentially useful pigment can be extracted from it.
        Do not claim that a product is safe based only on its ingredient list or appearance.
        Treat findings from previous experiments as evidence of artistic performance under those experimental conditions, not proof of general safety.
        Mention relevant handling precautions and uncertainties when appropriate.
        Do not assume that all products of the same cosmetic type will produce identical results.

        RESPONSE STYLE
        Write in clear, accessible English.
        Use descriptive subheadings and concise bullet points where helpful.
        Keep the two main sections clearly separated.
        Focus on practical suggestions on specific products rather than generic explanations.
        Do not provide an unnecessarily long step-by-step tutorial.
        Avoid unnecessary repetition. 
        """

        if uploaded_image is not None:
            image_bytes = uploaded_image.getvalue()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            image_type = uploaded_image.type
           
        
        if input_method == "Upload a photo":
            user_content = [
                {"type":"text","text": prompt + "\n\nPlease carefully read the uploaded image and extract the cosmetic ingredients list."},
                {"type":"image_url","image_url": {"url": f"data:{image_type};base64,{base64_image}"}} 
                ]
        
        else:
            user_content = [
                {"type":"text","text": prompt}
            ]
        
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant for CosmeticCycle, a project that explores reusing expired cosmetics as drawing materials."
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        )
        

        st.write(response.choices[0].message.content)
