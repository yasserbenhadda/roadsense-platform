import { Injectable } from '@nestjs/common';
import { Express } from 'express';
import { randomUUID } from 'crypto';
import * as fs from 'fs';
import { ProcessingService } from '../processing/processing.service';

@Injectable()
export class UploadService {

    constructor(private readonly processingService: ProcessingService) { }

    async handleUpload(file: any) {

        const jobId = randomUUID();
        const filePath = `uploads/${jobId}.mp4`;

        // Sauvegarde en local
        fs.writeFileSync(filePath, file.buffer);

        // Appeler ProcessingService
        this.processingService.processVideo(jobId, filePath);

        return jobId;
    }
}
