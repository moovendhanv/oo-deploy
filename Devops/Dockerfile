FROM public.ecr.aws/lambda/nodejs:20

# Copy and install
COPY package*.json ./
RUN npm install --omit=dev

COPY index.mjs ./

# Default CMD for AWS Batch (Node handler)
CMD ["index.mjs"]
