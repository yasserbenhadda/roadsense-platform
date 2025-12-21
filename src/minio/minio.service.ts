import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as Minio from 'minio';
import * as fs from 'fs';

@Injectable()
export class MinioService {
    private readonly logger = new Logger(MinioService.name);
    private minioClient: Minio.Client;

    constructor(private configService: ConfigService) {
        this.minioClient = new Minio.Client({
            endPoint: this.configService.get<string>('MINIO_ENDPOINT', 'localhost'),
            port: parseInt(this.configService.get<string>('MINIO_PORT', '9000'), 10),
            useSSL: this.configService.get<string>('MINIO_USE_SSL') === 'true',
            accessKey: this.configService.get<string>('MINIO_ROOT_USER', 'roadsense'),
            secretKey: this.configService.get<string>('MINIO_ROOT_PASSWORD', 'roadsense123'),
        });
    }

    async uploadVideo(bucket: string, key: string, filePath: string): Promise<void> {
        await this.ensureBucket(bucket);
        await this.minioClient.fPutObject(bucket, key, filePath);
        this.logger.log(`Uploaded video to ${bucket}/${key}`);
    }

    async uploadFrame(bucket: string, key: string, filePath: string): Promise<void> {
        await this.ensureBucket(bucket);
        await this.minioClient.fPutObject(bucket, key, filePath);
    }

    async uploadJson(bucket: string, key: string, data: any): Promise<void> {
        await this.ensureBucket(bucket);
        const jsonString = JSON.stringify(data);
        await this.minioClient.putObject(bucket, key, jsonString, jsonString.length, {
            'Content-Type': 'application/json',
        });
        this.logger.log(`Uploaded JSON to ${bucket}/${key}`);
    }

    private async ensureBucket(bucket: string): Promise<void> {
        const exists = await this.minioClient.bucketExists(bucket);
        if (!exists) {
            await this.minioClient.makeBucket(bucket, 'us-east-1');
            this.logger.log(`Created bucket ${bucket}`);
        }
    }
}
