import { Injectable, Logger } from '@nestjs/common';
import ffmpeg from 'fluent-ffmpeg';
import * as fs from 'fs';
import * as path from 'path';
import { exiftool } from 'exiftool-vendored';
import { MinioService } from '../minio/minio.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class ProcessingService {
    private readonly logger = new Logger(ProcessingService.name);

    constructor(
        private readonly minioService: MinioService,
        private readonly configService: ConfigService,
    ) { }

    async processVideo(jobId: string, videoPath: string): Promise<void> {
        this.logger.log(`Starting video processing for job ${jobId}`);

        const outputDir = path.join('tmp', 'frames', jobId);

        // Create output directory if it doesn't exist
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        return new Promise((resolve, reject) => {
            ffmpeg(videoPath)
                .outputOptions([
                    '-vf', 'fps=1', // 1 frame/sec
                    '-qscale:v', '2', // quality
                ])
                .output(path.join(outputDir, 'frame-%06d.jpg'))
                .on('end', async () => {
                    this.logger.log(`Frames extracted successfully for job ${jobId}`);

                    try {
                        await this.processFrames(jobId, outputDir);
                        resolve();
                    } catch (error) {
                        this.logger.error(`Error processing frames: ${error.message}`);
                        reject(error);
                    }
                })
                .on('error', (err) => {
                    this.logger.error(`Error processing video for job ${jobId}: ${err.message}`);
                    reject(err);
                })
                .run();
        });
    }

    private async processFrames(jobId: string, outputDir: string) {
        const files = fs.readdirSync(outputDir).filter(f => f.endsWith('.jpg'));
        const framesMetadata: any[] = [];
        const bucket = this.configService.get<string>('MINIO_BUCKET_FRAMES', 'frames');

        for (const file of files) {
            const framePath = path.join(outputDir, file);

            // Read EXIF
            const meta = await exiftool.read(framePath);
            const gps = {
                lat: meta.GPSLatitude,
                lon: meta.GPSLongitude,
            };
            const timestamp = meta.DateTimeOriginal || meta.CreateDate;

            framesMetadata.push({
                frameName: file,
                gps,
                timestamp,
            });

            // Upload frame to Minio
            await this.minioService.uploadFrame(bucket, `${jobId}/${file}`, framePath);
        }

        // Upload metadata JSON
        await this.minioService.uploadJson(bucket, `${jobId}/metadata.json`, framesMetadata);

        this.logger.log(`Processed ${files.length} frames and uploaded metadata for job ${jobId}`);
    }
}
